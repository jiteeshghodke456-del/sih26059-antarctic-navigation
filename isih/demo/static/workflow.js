/* The §4 passage workflow, driven entirely by the server's state machine.

   Two ECDIS modes, because that is the software these users already know:
   VOYAGE…APPROVED is Route Planning, ACTIVE and WORKSPACE are Route
   Monitoring. The workspace is not a third mode — it is monitoring with an
   alarm acknowledged and an edit pending, exactly what an operator gets when
   a monitored route trips an alarm and they open the route editor.

   There is one copy of workflow state and the server owns it. `W.doc` is the
   last /api/workflow document and nothing else holds stage, mission or voyage
   — so a page reload mid-passage re-hydrates to the same step, and an
   out-of-order click shows the server's own 409 reason rather than being
   hidden by a disabled button. */
(function () {
  'use strict';

  var C = window.ISIH.console;
  var $ = function (id) { return document.getElementById(id); };
  var W = { doc: null, prevStage: null, preview: new Map() };

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) { n.className = cls; }
    if (text !== undefined && text !== null) { n.textContent = text; }
    return n;
  }
  function show(id, on) { var n = $(id); if (n) { n.hidden = !on; } }

  function getJSON(u) {
    return fetch(u).then(function (r) {
      if (!r.ok) { throw new Error(r.status + ' from ' + u); }
      return r.json();
    });
  }

  function act(action, body) {
    return fetch('/api/workflow/' + action, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body || {})
    }).then(function (r) {
      return r.json().then(function (j) {
        if (!r.ok) {
          // A 409 means the workflow refused an out-of-order step. Show the
          // server's own sentence — a guard the user cannot see is a guard
          // they will not believe.
          var e = new Error(typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail));
          e.status = r.status;
          throw e;
        }
        return j;
      });
    }).then(apply).catch(function (e) {
      // Never swallow. A rendering bug here previously left the panel blank
      // with no message anywhere, which is far worse than an ugly error.
      if (!e.status) { console.error('workflow apply failed:', e); }
      var s = $('stage-error');
      if (s) { s.textContent = e.message; s.hidden = false; }
      var g = $('signin-state');
      if (g && W.doc && W.doc.stage === 'sign_in') {
        g.textContent = e.message; g.className = 'approve-state err';
      }
    });
  }

  // ---------- panel builders ----------

  function panel(title, asks) {
    var host = $('stage-panel');
    host.innerHTML = '';
    var head = el('div', 'phead');
    head.appendChild(el('h2', null, title));
    if (asks) { head.appendChild(el('p', 'src', asks)); }
    host.appendChild(head);
    var err = el('p', 'approve-state err'); err.id = 'stage-error'; err.hidden = true;
    host.appendChild(err);
    return host;
  }

  function primary(host, label, action, bodyFn) {
    var row = el('div', 'approw');
    var b = el('button', null, label);
    b.setAttribute('data-primary', '');
    b.setAttribute('data-action', action);
    b.addEventListener('click', function () {
      $('stage-error').hidden = true;
      act(action, bodyFn ? bodyFn() : {});
    });
    row.appendChild(b);
    host.appendChild(row);
    return b;
  }

  function kv(host, rows) {
    var dl = el('dl', 'kv');
    rows.forEach(function (r) {
      dl.appendChild(el('dt', null, r[0]));
      var dd = el('dd', 'wrap', r[1]); dl.appendChild(dd);
    });
    host.appendChild(dl);
    return dl;
  }

  // ---------- the stages ----------

  var stages = {
    sign_in: function () {
      show('signin-screen', true); show('passage-bar', false);
      document.querySelector('main.grid').hidden = true;
    },

    command_center: function (d) {
      var host = panel(d.title, d.asks);
      var v = d.voyage;
      kv(host, [
        ['Voyage on this device', v ? v.name : 'none yet'],
        ['Replay window', '1–31 December 2019, 31 daily files preflighted at start'],
        ['Sources', 'NOAA/NSIDC CDR G02202 v6 · PolarRoute 1.1.11 + meshiphi 2.3.1']
      ]);
      host.appendChild(el('p', 'note', 'The application starts from local files. ' +
        'Nothing on this screen needs the network.'));
      primary(host, v ? 'Start another voyage' : 'New voyage', 'new-voyage');
      var fut = el('a', 'linkish future-link', 'Future scope — Baymax Mode and the master\u2019s assistant (simulated)');
      fut.href = '/future';
      host.appendChild(fut);
      C.setLayers({ route: false, ship: false, waypoints: false,
                    straightLine: true, stations: true, protectedAreas: true });
      C.setDayLabel('browse the window');
    },

    voyage: function (d) {
      var host = panel(d.title, d.asks);
      var ch = d.choices || {};
      var name = el('input'); name.type = 'text'; name.id = 'v-name';
      name.value = '43rd ISEA resupply';
      var dest = el('select'); dest.id = 'v-dest';
      (ch.destinations || []).forEach(function (x) {
        var o = el('option', null, x); o.value = x; dest.appendChild(o);
      });
      var day = el('select'); day.id = 'v-day';
      (ch.days || []).forEach(function (x) {
        var o = el('option', null, C.h.longDate(x)); o.value = x; day.appendChild(o);
      });
      day.addEventListener('change', function () {
        C.setDay(C.dayIndexOf(day.value));
      });

      [['Voyage name', name], ['Destination', dest], ['Departure day', day]]
        .forEach(function (r) {
          var row = el('div', 'field');
          row.appendChild(el('label', null, r[0]));
          row.appendChild(r[1]);
          host.appendChild(row);
        });
      primary(host, 'Start voyage', 'voyage', function () {
        return { name: name.value, destination: dest.value, depart_day: day.value };
      });
      C.setDayLabel('departure day');
    },

    mission: function (d) {
      var host = panel(d.title, d.asks);
      var chosen = { v: 'STATION_REQUIRED' };
      ((d.choices || {}).policies || []).forEach(function (pol, i) {
        var wrap = el('label', 'choice');
        var r = el('input'); r.type = 'radio'; r.name = 'policy'; r.value = pol.value;
        r.checked = i === 0;
        r.addEventListener('change', function () { chosen.v = pol.value; });
        wrap.appendChild(r);
        var body = el('span');
        body.appendChild(el('b', null, pol.label));
        body.appendChild(el('span', 'choice-why', pol.consequence));
        wrap.appendChild(body);
        host.appendChild(wrap);
      });
      var cargo = el('input'); cargo.type = 'number'; cargo.id = 'm-cargo';
      cargo.placeholder = 'tonnes'; cargo.min = '0';
      var row = el('div', 'field');
      row.appendChild(el('label', null, 'Cargo'));
      row.appendChild(cargo);
      host.appendChild(row);
      host.appendChild(el('p', 'note',
        'This is the field that decides whether the voyage succeeded, and it ' +
        'changes the answer: on real December 2019 observations these two ' +
        'policies disagree on 23 of the 31 days.'));
      primary(host, 'Define mission', 'mission', function () {
        return { destination_policy: chosen.v,
                 cargo_tonnes: cargo.value ? parseInt(cargo.value, 10) : null };
      });
    },

    route: function (d) {
      var host = panel(d.title, d.asks);
      ((d.choices || {}).sources || []).forEach(function (src) {
        var card = el('div', 'choice static');
        var b = el('b', null, src.label);
        card.appendChild(b);
        card.appendChild(el('span', 'choice-why', src.detail));
        if (src.value === 'imported') { card.classList.add('disabled'); }
        host.appendChild(card);
      });
      primary(host, 'Solve route', 'route', function () { return { source: 'solved' }; });
      C.setLayers({ route: false, ship: false });
    },

    waypoints: function (d) {
      var host = panel(d.title, d.asks);
      var box = el('div', 'wp-scroll');
      host.appendChild(box);
      getJSON('/api/waypoints').then(function (w) {
        var t = el('table', 'vt');
        var head = el('tr');
        ['#', 'Position', 'Elapsed', 'ETA'].forEach(function (h) {
          head.appendChild(el('th', null, h));
        });
        var thead = el('thead'); thead.appendChild(head); t.appendChild(thead);
        var tb = el('tbody');
        w.waypoints.forEach(function (r) {
          var tr = el('tr');
          tr.appendChild(el('td', null, r.n));
          tr.appendChild(el('td', null, C.h.fmtPos(r.lat, r.lon)));
          tr.appendChild(el('td', null, r.elapsed_days === null ? '—' : r.elapsed_days.toFixed(2) + ' d'));
          tr.appendChild(el('td', null, r.eta || '—'));
          tb.appendChild(tr);
        });
        t.appendChild(tb); box.appendChild(t);
        host.insertBefore(el('p', 'note', w.note), box.nextSibling);
      });
      primary(host, 'Confirm waypoints and ETAs', 'waypoints');
      C.setLayers({ route: true, waypoints: true, ship: false });
    },

    review: function (d) {
      var host = panel(d.title, d.asks);
      C.setShowAssessment(true);
      show('health-band', true); show('assessment-subgrid', true);
      C.setLayers({ route: true, waypoints: true, ship: false });
      C.setDayLabel('look ahead');
      var who = el('input'); who.type = 'text'; who.id = 'wf-approver';
      who.value = d.watchkeeper || ''; who.readOnly = true;
      var why = el('input'); why.type = 'text'; why.id = 'wf-why';
      why.placeholder = 'Why is this acceptable? (optional)';
      var row = el('div', 'approw');
      row.appendChild(who); row.appendChild(why);
      host.appendChild(row);
      primary(host, 'Approve route', 'approve', function () {
        return { why: why.value };
      });
      if (d.voyage && d.voyage.depart_day) {
        C.loadDecision(d.voyage.depart_day);
      }
    },

    approved: function (d) {
      var host = panel(d.title, d.asks);
      var v = d.voyage || {}, r = d.route_plan || {};
      kv(host, [
        ['Voyage', v.name || '—'],
        ['Mission', (d.mission || {}).meaning || '—'],
        ['Departure', v.depart_day ? C.h.longDate(v.depart_day) : '—'],
        ['Route', (r.n_waypoints || '—') + ' waypoints, ' +
                  (r.total_days ? r.total_days.toFixed(2) + ' d' : '—')],
        ['Approved by', d.watchkeeper || '—']
      ]);
      primary(host, 'Begin navigation', 'navigate');
      show('log-panel', true);
    },

    active: function (d) {
      var host = panel(d.title, d.asks);
      C.setLayers({ route: true, waypoints: false, ship: true });
      C.setDayLabel('today');
      show('log-panel', true);
      var dec = C.decision();
      if (dec && dec.diverges_from_approval) {
        var b = el('div', 'headsup');
        b.appendChild(el('b', null, 'Heads-up'));
        b.appendChild(el('span', null, dec.divergence));
        host.appendChild(b);
      } else {
        host.appendChild(el('p', 'note',
          'The plan of record still matches the evidence. Move the day slider ' +
          'to keep checking.'));
      }
      primary(host, 'Open decision workspace', 'workspace', function () {
        var dd = C.decision();
        return { reason: (dd && dd.divergence) || 'reassessed on the master’s initiative' };
      });
    },

    workspace: function (d) {
      var host = panel(d.title, d.asks);
      C.setDayLabel('evidence as of this day');
      var dec = C.decision();

      if (dec && dec.divergence) {
        var b = el('div', 'headsup');
        b.appendChild(el('b', null, 'What changed'));
        b.appendChild(el('span', null, dec.divergence));
        host.appendChild(b);
      }

      var table = el('div', 'preview'); host.appendChild(table);
      renderPreview(table);
      // The day slider is the what-if lever while the workspace is open, so
      // the preview has to follow it.
      var slider = $('day');
      if (slider && !slider.dataset.wfBound) {
        slider.dataset.wfBound = '1';
        slider.addEventListener('input', function () {
          if (W.doc && W.doc.stage === 'workspace') {
            var t = document.querySelector('#stage-panel .preview');
            if (t) { renderPreview(t); }
          }
        });
      }

      // §4's three choices, in its order.
      var why = el('input'); why.type = 'text'; why.id = 'ws-why';
      why.placeholder = 'Why? (recorded in the decision log)';
      host.appendChild(el('p', 'note',
        'Corridors were solved on 1 Dec 2019 ice and held fixed. Changing the ' +
        'departure day changes the ETAs and the destination reading, not the ' +
        'geometry.'));
      var row = el('div', 'approw'); row.appendChild(why); host.appendChild(row);

      var choices = el('div', 'choices3');
      [['Keep plan', 'keep'], ['Edit plan', 'edit'], ['Take corridor B', 'alternative']]
        .forEach(function (c) {
          var btn = el('button', null, c[0]);
          btn.setAttribute('data-action', c[1]);
          if (c[1] === 'keep') { btn.setAttribute('data-primary', ''); }
          btn.addEventListener('click', function () {
            $('stage-error').hidden = true;
            var body = { why: why.value, day: C.currentDate() };
            if (c[1] === 'edit') { body.what = 'departure day ' + C.currentDate(); body.depart_day = C.currentDate(); }
            if (c[1] === 'alternative') { body.label = 'B'; }
            act(c[1], body);
          });
          choices.appendChild(btn);
        });
      host.appendChild(choices);
    }
  };

  function renderPreview(host) {
    host.innerHTML = '';
    var day = C.currentDate();
    getJSON('/api/preview?day=' + day).then(function (pv) {
      var t = el('table', 'vt');
      var hr = el('tr');
      ['Corridor', 'Legs', 'Steaming', 'Δ', 'Worst ice / limit', 'Ice gate', 'Arrives', 'Destination then']
        .forEach(function (h) { hr.appendChild(el('th', null, h)); });
      var th = el('thead'); th.appendChild(hr); t.appendChild(th);
      var tb = el('tbody');
      pv.corridors.forEach(function (c) {
        var tr = el('tr');
        if (!c.solved) { tr.className = 'unsolved'; }
        tr.appendChild(el('td', null, c.label + ' — ' + c.name));
        tr.appendChild(el('td', null, c.solved ? c.legs : '—'));
        tr.appendChild(el('td', null, c.solved ? c.traveltime_days.toFixed(2) + ' d' : 'no route'));
        tr.appendChild(el('td', null,
          (c.eta_delta_days === undefined || c.eta_delta_days === null)
            ? (c.solved ? 'ref' : '—')
            : (c.eta_delta_days > 0 ? '+' : '') + c.eta_delta_days.toFixed(2) + ' d'));
        tr.appendChild(el('td', null, c.solved
          ? (c.worst_ice_pct + '% / ' + c.ice_limit_pct + '%')
          : 'limit ' + c.ice_limit_pct + '% closes it'));
        var g = el('td', null, c.ice_gate || '—');
        if (c.ice_gate) { g.className = 'gcell s-' + c.ice_gate; }
        tr.appendChild(g);
        tr.appendChild(el('td', null, c.arrival_day ? C.h.longDate(c.arrival_day) : '—'));
        var dest = el('td', null, c.destination_on_arrival);
        if (c.destination_on_arrival === 'closed') { dest.className = 'gcell s-FAIL'; }
        if (c.destination_on_arrival === 'open') { dest.className = 'gcell s-PASS'; }
        tr.appendChild(dest);
        tb.appendChild(tr);
      });
      t.appendChild(tb); host.appendChild(t);
      host.appendChild(el('p', 'src',
        'Departing ' + C.h.longDate(pv.day) + ' · destination read as ' + pv.target +
        ' · ' + pv.router));
      host.appendChild(el('p', 'note', pv.scope));
    }).catch(function (e) {
      host.appendChild(el('p', 'note', 'Preview unavailable: ' + e.message));
    });
  }

  function renderVoyageFacts(d) {
    var host = $('voyage-facts');
    if (!host) { return; }
    host.innerHTML = '';
    var v = d.voyage, m = d.mission, r = d.route_plan;
    [['Watchkeeper', d.watchkeeper || '—'],
     ['Voyage', v ? v.name : 'not started'],
     ['Destination', v ? v.destination : '—'],
     ['Departure', v && v.depart_day ? C.h.longDate(v.depart_day) : '—'],
     ['Mission', m ? m.meaning : 'not defined'],
     ['Route', r ? (r.n_waypoints + ' waypoints, ' +
       (r.total_days ? r.total_days.toFixed(2) + ' d' : '—')) : 'not solved'],
     ['Waypoints', d.waypoints_confirmed ? 'confirmed' : 'not confirmed']
    ].forEach(function (row) {
      host.appendChild(el('dt', null, row[0]));
      host.appendChild(el('dd', 'wrap', row[1]));
    });
  }

  // ---------- the passage bar ----------

  function renderBar(d) {
    C.h.txt('wf-step', d.step_number); C.h.txt('wf-count', d.step_count);
    C.h.txt('wf-title', d.title); C.h.txt('wf-asks', d.asks);
    C.h.txt('wf-watch', d.watchkeeper ? 'Watch: ' + d.watchkeeper : '');
    C.h.txt('wf-mode', d.mode === 'monitoring' ? 'ROUTE MONITORING' : 'ROUTE PLANNING');
    var host = $('wf-steps'); host.innerHTML = '';
    d.order.forEach(function (o, i) {
      var li = el('li', o.done ? 'done' : (i === d.step_number - 1 ? 'now' : ''));
      li.title = o.title;
      host.appendChild(li);
    });
  }

  // ---------- apply ----------

  function apply(d) {
    W.doc = d;
    var changed = d.stage !== W.prevStage;
    W.prevStage = d.stage;

    if (d.stage !== 'sign_in') {
      show('signin-screen', false);
      document.querySelector('main.grid').hidden = false;
      show('passage-bar', true);
      renderBar(d);
    }
    if (d.voyage && d.voyage.depart_day) {
      C.setDepartIndex(C.dayIndexOf(d.voyage.depart_day));
    }

    // Nothing assessed may appear before the route has been reviewed, and
    // nothing about the ship before it has sailed. Showing gates and an
    // approval box while the mission is still being defined would invite a
    // judge to approve a route that does not exist yet.
    var planning = ['sign_in', 'command_center', 'voyage', 'mission', 'route', 'waypoints'];
    var isPlanning = planning.indexOf(d.stage) >= 0;
    var underWay = d.stage === 'active' || d.stage === 'workspace';

    if (isPlanning) { C.setShowAssessment(false); }
    show('health-band', !isPlanning);
    show('assessment-subgrid', !isPlanning);
    show('log-panel', !isPlanning);
    show('rail-voyage', isPlanning && d.stage !== 'sign_in');
    show('rail-gates', !isPlanning);
    show('rail-alts', !isPlanning);
    show('rail-fresh', !isPlanning);
    show('rail-ship', underWay);
    show('rail-approve', false);          // approval lives in the stage panel now
    if (isPlanning && d.stage !== 'sign_in') { renderVoyageFacts(d); }

    show('stage-panel', d.stage !== 'sign_in');
    (stages[d.stage] || function () {})(d);
    if (changed) { window.scrollTo({ top: 0, behavior: 'instant' }); }
  }

  // ---------- boot ----------

  $('signin-btn').addEventListener('click', function () {
    var n = $('signin-name').value.trim();
    if (!n) {
      $('signin-state').textContent =
        'Enter a name and rank. An approval nobody signed is not an approval.';
      $('signin-state').className = 'approve-state err';
      return;
    }
    act('sign-in', { name: n });
  });
  $('signin-name').addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { $('signin-btn').click(); }
  });
  $('wf-cc').addEventListener('click', function () { act('command-center', {}); });

  C.setShowAssessment(false);
  getJSON('/api/workflow').then(apply).catch(function (e) {
    var s = $('signin-state');
    if (s) { s.textContent = 'Workflow unavailable: ' + e.message; s.hidden = false; }
  });
})();
