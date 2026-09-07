/* The future-scope screen: Baymax Mode and the master's assistant.

   Two rules govern this file.

   1. The physiological values are a FIXED sequence, not random. A randomised
      readout looks like a live feed, and something that looks live is the one
      thing §25 forbids. A fixed loop reads as a demonstration, which is what
      it is.

   2. The assistant composes its answers from /api/decision — the same object
      the bridge console serves — and says so. It is templated retrieval over
      real state, not generation. Faking model output to look impressive would
      undermine every real number on the other screen. */
(function () {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) { n.className = cls; }
    if (text !== undefined && text !== null) { n.textContent = text; }
    return n;
  }

  // ---------- Baymax: a fixed watch, not a feed ----------
  // One scripted watch, 20:00 to 04:00 — the middle watch, which is when
  // fatigue actually bites. Values are illustrative and stated as such.
  var WATCH = [
    { t: '20:00', hr: 62, hrv: 58, spo2: 98, sleep: 7.1, load: 'settled' },
    { t: '22:00', hr: 66, hrv: 51, spo2: 98, sleep: 7.1, load: 'settled' },
    { t: '00:00', hr: 71, hrv: 43, spo2: 97, sleep: 7.1, load: 'rising' },
    { t: '02:00', hr: 78, hrv: 34, spo2: 97, sleep: 7.1, load: 'elevated' },
    { t: '04:00', hr: 74, hrv: 38, spo2: 98, sleep: 7.1, load: 'elevated' }
  ];

  var SUGGESTS = [
    ['Take four slow breaths before the next fix.',
     'Paced breathing is the one intervention with a plausible effect inside a watch.'],
    ['Two minutes off the screen, eyes to the horizon.',
     'Dark adaptation and screen glare are a real bridge problem, not a wellness slogan.'],
    ['Queue something without vocals for the last hour.',
     'A preference, offered — never played without being asked.'],
    ['You have held this watch through a route change. That was the right call to escalate.',
     'Words of comfort, §25. Specific to what happened, or it is noise.']
  ];

  function renderVitals() {
    var host = $('vitals');
    host.innerHTML = '';
    WATCH.forEach(function (w, i) {
      var card = el('div', 'vital' + (w.load === 'elevated' ? ' warn' : ''));
      card.appendChild(el('span', 'vital-t', w.t));
      var g = el('div', 'vital-grid');
      [['HR', w.hr + ' bpm'], ['HRV', w.hrv + ' ms'],
       ['SpO₂', w.spo2 + ' %'], ['Sleep', w.sleep + ' h']].forEach(function (r) {
        g.appendChild(el('span', 'vk', r[0]));
        g.appendChild(el('span', 'vv', r[1]));
      });
      card.appendChild(g);
      card.appendChild(el('span', 'vital-load', 'workload ' + w.load));
      host.appendChild(card);
    });
    var note = el('p', 'src',
      'A fixed demonstration watch (20:00–04:00), not a feed. The same five ' +
      'cards appear on every load, deliberately — nothing here is measured.');
    host.parentNode.insertBefore(note, host.nextSibling);
  }

  function renderSuggests() {
    var host = $('suggests');
    host.innerHTML = '';
    SUGGESTS.forEach(function (s) {
      var li = document.createElement('li');
      li.appendChild(el('b', null, s[0]));
      li.appendChild(el('span', 'choice-why', s[1]));
      host.appendChild(li);
    });
  }

  // ---------- the assistant: templated over real state ----------
  var QUESTIONS = [
    {
      q: 'Is the route still good?',
      a: function (d) {
        if (!d) { return 'I cannot read the decision object — the console may not be running.'; }
        var s = 'Route health is ' + d.health + '. ';
        if (d.top_reasons && d.top_reasons.length) { s += d.top_reasons[0] + '. '; }
        if (d.diverges_from_approval) { s += d.divergence + '.'; }
        else if (d.approved_version) { s += 'Nothing has changed since it was approved.'; }
        else { s += 'It has not been approved yet.'; }
        return s;
      }
    },
    {
      q: 'What don’t you know?',
      a: function (d) {
        if (!d) { return 'I cannot read the decision object.'; }
        var unk = d.gates.filter(function (g) { return g.state === 'UNKNOWN'; });
        return unk.length + ' of ' + d.gates.length + ' gates have no data behind them: ' +
          unk.map(function (g) { return g.gate; }).join(', ') +
          '. That is why I will not call this route valid.';
      }
    },
    {
      q: 'What are my alternatives?',
      a: function (d) {
        if (!d || !d.alternatives.length) { return 'No alternative corridor has been computed.'; }
        return d.alternatives.map(function (a) {
          return a.label + ' — ' + a.summary;
        }).join('  |  ');
      }
    },
    {
      q: 'Why can’t I trust the ice limit?',
      a: function () {
        return 'Because no ice class indexes ice concentration. Every framework — ' +
          'IACS Polar Class, the Russian Register rules, the Finnish-Swedish rules, ' +
          'POLARIS — indexes thickness or ice type. The 80 % figure is our working ' +
          'assumption, not a certificated limit, and the corridors show what happens ' +
          'when it is tightened.';
      }
    },
    {
      q: 'What would change your mind?',
      a: function (d) {
        if (!d || !d.trigger_conditions.length) { return 'No trigger conditions are recorded.'; }
        return d.trigger_conditions.join('; ') + '.';
      }
    }
  ];

  function ask(item, decision) {
    var chat = $('chat');
    chat.appendChild(el('div', 'bubble you', item.q));
    var a = el('div', 'bubble sys');
    a.appendChild(el('span', null, item.a(decision)));
    a.appendChild(el('span', 'bubble-src',
      'Composed from /api/decision. Templated, not generated.'));
    chat.appendChild(a);
    chat.scrollTop = chat.scrollHeight;
  }

  function boot(decision) {
    renderVitals();
    renderSuggests();
    var host = $('asklist');
    QUESTIONS.forEach(function (item) {
      var b = el('button', 'askbtn', item.q);
      b.addEventListener('click', function () { ask(item, decision); });
      host.appendChild(b);
    });
    ask(QUESTIONS[0], decision);
  }

  fetch('/api/decision')
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(boot)
    .catch(function () { boot(null); });
})();
