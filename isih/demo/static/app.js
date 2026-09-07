/* ISIH bridge console — plain JS, no libraries, no network beyond this server.
   Canvas draws the satellite ice raster; SVG draws the route and stations.
   Both share one lat/lon projection so they cannot drift apart.

   The panels below the chart are driven by /api/decision, so what the screen
   says about route health and the nine gates is the same object the API
   serves — there is no second, friendlier copy of the truth in the UI. */
(function () {
  'use strict';

  var S = { summary: null, route: null, decision: null, dayIdx: 0, qa: 'on',
            cache: new Map(), field: null, paShow: true };
  var $ = function (id) { return document.getElementById(id); };

  // ---------- errors are shown, never swallowed ----------
  function fail(msg) {
    var e = $('error'); e.textContent = 'Demo error: ' + msg; e.hidden = false;
  }
  window.addEventListener('error', function (ev) { fail(ev.message); });

  function getJSON(url) {
    return fetch(url).then(function (r) {
      if (!r.ok) { throw new Error(r.status + ' from ' + url); }
      return r.json();
    });
  }
  function postJSON(url, body) {
    return fetch(url, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    }).then(function (r) {
      return r.json().then(function (j) {
        if (!r.ok) { throw new Error(j.detail ? JSON.stringify(j.detail) : r.status); }
        return j;
      });
    });
  }

  function txt(id, v) { var n = $(id); if (n) { n.textContent = v; } }
  function elDiv(cls, text) {
    var d = document.createElement('div');
    if (cls) { d.className = cls; }
    if (text !== undefined) { d.textContent = text; }
    return d;
  }

  // ---------- projection ----------
  var B;
  var canvas = $('ice'), ctx = canvas.getContext('2d'), svg = $('vec'), wrap = $('map-wrap');
  var W = 0, H = 0, DPR = 1;

  function sizeCanvas() {
    var r = wrap.getBoundingClientRect();
    DPR = window.devicePixelRatio || 1;
    W = Math.max(1, Math.round(r.width)); H = Math.max(1, Math.round(r.height));
    canvas.width = W * DPR; canvas.height = H * DPR;
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
  }
  function px(lon, lat) {
    return [ (lon - B.lon_min) / (B.lon_max - B.lon_min) * W,
             (B.lat_max - lat) / (B.lat_max - B.lat_min) * H ];
  }

  // ---------- colour ramp (same stops as the CSS legend) ----------
  var STOPS = [[0,[242,247,252]],[25,[198,219,239]],[50,[107,174,214]],[75,[33,113,181]],[100,[8,48,107]]];
  function ramp(p) {
    p = Math.max(0, Math.min(100, p));
    for (var i = 1; i < STOPS.length; i++) {
      if (p <= STOPS[i][0]) {
        var a = STOPS[i-1], b = STOPS[i], t = (p - a[0]) / (b[0] - a[0]);
        var c = [0,1,2].map(function (k) { return Math.round(a[1][k] + (b[1][k] - a[1][k]) * t); });
        return 'rgb(' + c.join(',') + ')';
      }
    }
    return 'rgb(8,48,107)';
  }

  // ---------- ice raster ----------
  function drawIce(f) {
    ctx.clearRect(0, 0, W, H);
    if (!f) { return; }
    var s = Math.max(3, Math.round(H / ((B.lat_max - B.lat_min) / 0.45)));
    var half = s / 2, i, p;
    for (i = 0; i < f.lat.length; i++) {
      p = px(f.lon[i], f.lat[i]);
      ctx.fillStyle = ramp(f.sic[i]);
      ctx.fillRect(p[0] - half, p[1] - half, s, s);
    }
    ctx.strokeStyle = '#C97B1E'; ctx.lineWidth = 1.2;
    for (i = 0; i < f.unknown_lat.length; i++) {
      p = px(f.unknown_lon[i], f.unknown_lat[i]);
      ctx.strokeRect(p[0] - half + 0.6, p[1] - half + 0.6, s - 1.2, s - 1.2);
    }
  }

  // ---------- vectors ----------
  function el(name, attrs, text) {
    var n = document.createElementNS('http://www.w3.org/2000/svg', name);
    Object.keys(attrs).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (text !== undefined) { n.textContent = text; }
    return n;
  }

  var paMarked = 0;
  function drawProtected() {
    // Drawn first, so it sits beneath the route and the stations. A legal
    // constraint layer should be legible without ever competing with the
    // navigation picture — master prompt §2.2 and §48A.27.
    if (!S.protected || !S.protected.available || !S.paShow) { paMarked = 0; return; }

    // These areas are 0.3 to 250 km across on a map spanning 65 degrees of
    // longitude, so most are a pixel or two. Anything below MIN_PX is
    // substituted with a point symbol at its centre — ordinary cartographic
    // practice at small scale, stated in the footnote rather than left for
    // the viewer to infer. The polygon is still drawn at true size beneath.
    var MIN_PX = 9;
    paMarked = 0;

    S.protected.areas.forEach(function (a) {
      var isAsma = a.kind === 'ASMA';
      var col = isAsma ? '#7B4BA8' : '#A8434B';
      var xs = [], ys = [];

      a.rings.forEach(function (ring) {
        var d = ring.map(function (c, i) {
          var q = px(c[0], c[1]);
          xs.push(q[0]); ys.push(q[1]);
          return (i ? 'L' : 'M') + q[0].toFixed(1) + ' ' + q[1].toFixed(1);
        }).join(' ') + ' Z';
        svg.appendChild(el('path', {
          d: d, fill: col, 'fill-opacity': 0.13, stroke: col, 'stroke-width': 1.3,
          'stroke-dasharray': isAsma ? '5 3' : '', 'vector-effect': 'non-scaling-stroke'
        }));
      });

      if (!xs.length) { return; }
      var w = Math.max.apply(null, xs) - Math.min.apply(null, xs);
      var h = Math.max.apply(null, ys) - Math.min.apply(null, ys);
      if (Math.max(w, h) >= MIN_PX) { return; }

      paMarked++;
      var cx = (Math.max.apply(null, xs) + Math.min.apply(null, xs)) / 2;
      var cy = (Math.max.apply(null, ys) + Math.min.apply(null, ys)) / 2;
      svg.appendChild(el('circle', {
        cx: cx.toFixed(1), cy: cy.toFixed(1), r: 5.5,
        fill: col, 'fill-opacity': 0.18, stroke: col, 'stroke-width': 1.4,
        'stroke-dasharray': isAsma ? '4 2.5' : ''
      }));
      svg.lastChild.appendChild(el('title', {}, a.kind + ' ' + a.number + ' — ' + a.name));
    });
  }

  function drawVectors() {
    while (svg.firstChild) { svg.removeChild(svg.firstChild); }
    if (!S.route || !S.summary) { return; }
    drawProtected();
    var st = {}; S.summary.stations.forEach(function (s) { st[s.role] = s; });
    var a = px(st.start.lon, st.start.lat), b = px(st.destination.lon, st.destination.lat);

    // straight line — why routing is needed at all, not a competing method
    svg.appendChild(el('line', { x1: a[0], y1: a[1], x2: b[0], y2: b[1],
      stroke: '#C97B1E', 'stroke-width': 1.6, 'stroke-dasharray': '6 5', opacity: 0.9 }));

    var d = S.route.coords.map(function (c, i) {
      var p = px(c[0], c[1]); return (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1);
    }).join(' ');
    svg.appendChild(el('path', { d: d, fill: 'none', stroke: '#FFFFFF', 'stroke-width': 5.5, 'stroke-linejoin': 'round', opacity: 0.85 }));
    svg.appendChild(el('path', { d: d, fill: 'none', stroke: '#0E7A4A', 'stroke-width': 3, 'stroke-linejoin': 'round' }));

    function marker(s, dy, anchor) {
      var p = px(s.lon, s.lat);
      var hollow = s.role === 'approach';
      svg.appendChild(el('circle', { cx: p[0], cy: p[1], r: hollow ? 4.5 : 6, fill: hollow ? '#FFFFFF' : '#12303D', stroke: hollow ? '#4A6472' : '#FFFFFF', 'stroke-width': 2 }));
      var label = s.name.toUpperCase().replace(' (100 KM N)', '');
      svg.appendChild(el('text', { x: p[0] + (anchor === 'end' ? -10 : 10), y: p[1] + dy,
        'text-anchor': anchor, 'font-size': hollow ? 10 : 12, 'font-weight': hollow ? 500 : 700,
        fill: '#12303D', 'paint-order': 'stroke', stroke: '#FFFFFF', 'stroke-width': 3 }, label));
    }
    marker(st.start, 4, 'start');
    marker(st.destination, 4, 'end');
    marker(st.approach, -8, 'end');

    updatePaNote();
  }

  function updatePaNote() {
    var pa = S.protected;
    if (!pa || !pa.available) {
      txt('pa-note', 'Protected-area extract not generated — run isih/protected_areas.py.');
      return;
    }
    var c = pa.counts;
    var scale = paMarked
      ? paMarked + ' area' + (paMarked === 1 ? '' : 's') + ' smaller than the map scale are shown as markers. '
      : '';
    txt('pa-note', pa.transit_finding + ' ' + scale +
      c.polygons + ' polygons in the corridor (' + c.aspa_polygons + ' ASPA, ' +
      c.asma_polygons + ' ASMA, ' + c.marine + ' marine). Source: ' + pa.source);
  }

  // ---------- the decision ----------
  function renderHealth(dec) {
    var band = $('health-band');
    band.setAttribute('data-health', dec.health);
    txt('health-state', dec.health);
    txt('health-note', dec.top_reasons && dec.top_reasons.length
      ? dec.top_reasons[0] : 'All evaluated gates pass.');
    txt('health-binding', dec.binding_gates && dec.binding_gates.length
      ? 'Binding: ' + dec.binding_gates.join(', ')
      : '');

    // §48A.13: a route becomes unhealthy because an assumption changed, not
    // because new data arrived. Identical evidence yields an identical gate
    // digest and therefore no banner at all.
    var dv = $('health-diverge');
    if (dec.diverges_from_approval && dec.divergence) {
      dv.textContent = dec.divergence;
      dv.hidden = false;
    } else {
      dv.hidden = true;
    }

    var evaluated = dec.gates.filter(function (g) { return g.state !== 'UNKNOWN'; }).length;
    var bar = $('cov-bar'); bar.innerHTML = '';
    dec.gates.forEach(function (g) {
      var i = document.createElement('i');
      if (g.state !== 'UNKNOWN') { i.className = 'has'; }
      i.title = g.gate + ': ' + g.state;
      bar.appendChild(i);
    });
    txt('cov-text', evaluated + ' of ' + dec.gates.length +
      ' — the rest have no data behind them');
  }

  function renderGates(dec) {
    var host = $('gate-list'); host.innerHTML = '';
    dec.gates.forEach(function (g) {
      var li = document.createElement('li');
      li.className = 's-' + g.state;
      li.appendChild(elDiv('dot'));
      var mid = elDiv('');
      mid.appendChild(elDiv('g-name', g.gate));
      mid.appendChild(elDiv('g-why', g.reason));
      li.appendChild(mid);
      li.appendChild(elDiv('g-state', g.state));
      li.title = g.question;
      host.appendChild(li);
    });
  }

  function renderAlternatives(dec) {
    var host = $('alt-list'); host.innerHTML = '';
    if (!dec.alternatives.length) {
      host.appendChild(elDiv('a-sum', 'No alternative corridor has been computed.'));
      return;
    }
    dec.alternatives.forEach(function (a) {
      var li = document.createElement('li');
      var solved = a.eta_days !== null && a.eta_days !== undefined;
      if (!solved) { li.className = 'unsolved'; }
      var top = elDiv('a-top');
      top.appendChild(elDiv('a-label', a.label));
      var delta;
      if (!solved) {
        delta = 'no route';
      } else if (a.eta_delta_days === null || a.eta_delta_days === undefined) {
        delta = '';
      } else if (Math.abs(a.eta_delta_days) < 0.005) {
        delta = 'reference';           // the corridor the others are measured against
      } else {
        delta = (a.eta_delta_days > 0 ? '+' : '') + a.eta_delta_days.toFixed(2) + ' d';
      }
      top.appendChild(elDiv('a-delta', delta));
      li.appendChild(top);
      li.appendChild(elDiv('a-sum', a.summary));
      li.appendChild(elDiv('a-why', a.rationale));
      host.appendChild(li);
    });
  }

  function renderRisks(dec) {
    // §48A.5: physical hazard, vessel capability, route exposure and decision
    // uncertainty are four different things and must stay four things.
    var g = {}; dec.gates.forEach(function (x) { g[x.gate] = x; });
    var env = dec.environmental_state || {};
    var unknown = dec.gates.filter(function (x) { return x.state === 'UNKNOWN'; }).length;

    var rows = [
      ['Physical hazard', 'What is out there',
       'Sea ice observed at ' + (env.worst_ice_pct_on_route === null || env.worst_ice_pct_on_route === undefined
         ? 'an unsampled level' : env.worst_ice_pct_on_route.toFixed(0) + '% peak along the route') +
       '. Icebergs and weather are not on this screen.'],
      ['Vessel capability', 'What this ship can take',
       g.capability ? g.capability.reason : '—'],
      ['Route exposure', 'How much and for how long',
       (env.steaming_days ? env.steaming_days.toFixed(2) + ' days of steaming' : '—') +
       '; the router has no time dimension, so exposure is computed on one frozen ice field.'],
      ['Decision uncertainty', 'How much we cannot see',
       unknown + ' of ' + dec.gates.length + ' gates cannot be evaluated. This is why the route is not VALID.']
    ];
    var host = $('risk-list'); host.innerHTML = '';
    rows.forEach(function (r) {
      var li = document.createElement('li');
      li.appendChild(elDiv('r-name', r[0]));
      li.appendChild(elDiv('r-val', r[2]));
      li.title = r[1];
      host.appendChild(li);
    });
  }

  function renderFreshness(dec) {
    var host = $('freshness'); host.innerHTML = '';
    var env = dec.environmental_state || {};
    var rows = [
      ['Ice observation', env.ice_date || '—'],
      ['Ice source', env.ice_source || '—'],
      ['Router', env.router || '—'],
      ['Data mode', dec.data_mode],
      ['Live sensors', 'none — this is replay']
    ];
    rows.forEach(function (r) {
      var dt = document.createElement('dt'); dt.textContent = r[0];
      var dd = document.createElement('dd'); dd.textContent = r[1]; dd.className = 'wrap';
      host.appendChild(dt); host.appendChild(dd);
    });
  }

  function renderLog() {
    return getJSON('/api/decisions').then(function (d) {
      var host = $('log-list'); host.innerHTML = '';
      if (!d.entries.length) { host.appendChild(elDiv('l-meta', 'No decisions yet.')); return; }
      d.entries.forEach(function (e) {
        var li = document.createElement('li');
        var top = elDiv('l-top');
        top.appendChild(elDiv('l-ver', 'Version ' + e.route_version + ' — ' + e.health));
        top.appendChild(elDiv(e.approval.approved ? 'l-appr' : 'l-meta',
          e.approval.approved ? 'approved' : 'not approved'));
        li.appendChild(top);
        var meta = e.approval.approved
          ? 'by ' + e.approval.by + ' at ' + e.approval.at
          : (e.top_reasons[0] || '');
        li.appendChild(elDiv('l-meta', meta));
        if (e.supersedes) { li.appendChild(elDiv('l-meta', 'supersedes ' + e.supersedes)); }
        host.appendChild(li);
      });
    });
  }

  function renderDecision(dec) {
    S.decision = dec;
    renderHealth(dec);
    renderGates(dec);
    renderAlternatives(dec);
    renderRisks(dec);
    renderFreshness(dec);

    var v = dec.vessel_state || {};
    txt('limit', v.max_ice_conc);
    txt('v-class', v.ice_class || 'not recorded');
    txt('v-cat', v.polar_ship_category || 'not published — unverified');
    txt('v-pos', v.position_source || '—');

    // The question a bridge asks is not "was this object approved" — every
    // fresh evaluation is unapproved by construction — but "is the plan we
    // are sailing still the approved one". Those differ the moment the
    // evidence moves, and that is exactly when the master needs telling.
    var av = dec.approved_version;
    var st = $('approve-state');
    if (!av) {
      st.textContent = 'Not approved.';
      st.className = 'approve-state';
    } else if (dec.diverges_from_approval) {
      st.textContent = 'Approved by ' + av.by + ' on ' + av.day +
        ', but the evidence has moved since. Re-approval required.';
      st.className = 'approve-state err';
    } else {
      st.textContent = 'Approved by ' + av.by + ' at ' + av.at +
        ' (version ' + av.route_version + ').';
      st.className = 'approve-state done';
    }
  }

  function renderVesselTest(v) {
    var host = $('vessel-test'); host.innerHTML = '';
    var names = Object.keys(v.runs);
    var tbl = document.createElement('table'); tbl.className = 'vt';
    var thead = document.createElement('thead');
    var hr = document.createElement('tr');
    ['Vessel', 'Service speed', 'Beam', 'Steaming', 'Fuel'].forEach(function (h) {
      var th = document.createElement('th'); th.textContent = h; hr.appendChild(th);
    });
    thead.appendChild(hr); tbl.appendChild(thead);

    var tb = document.createElement('tbody');
    names.forEach(function (n) {
      var r = v.runs[n], c = r.config || {};
      var tr = document.createElement('tr');
      [n,
       (c.max_speed / 1.852).toFixed(1) + ' kn',
       c.beam + ' m',
       r.solved ? r.traveltime_days.toFixed(2) + ' d' : 'no route',
       r.solved ? r.fuel.toFixed(0) : '—'
      ].forEach(function (val, i) {
        var td = document.createElement('td'); td.textContent = val;
        if (i === 0) { td.style.fontWeight = '600'; }
        tr.appendChild(td);
      });
      tb.appendChild(tr);
    });

    var dr = document.createElement('tr');
    ['Difference', '', '',
     (v.eta_delta_days > 0 ? '+' : '') + v.eta_delta_days.toFixed(2) + ' d',
     (v.fuel_delta_pct > 0 ? '+' : '') + v.fuel_delta_pct.toFixed(1) + ' %'
    ].forEach(function (val, i) {
      var td = document.createElement('td'); td.textContent = val;
      if (i === 0 || i >= 3) { td.className = 'delta'; }
      dr.appendChild(td);
    });
    tb.appendChild(dr);
    tbl.appendChild(tb);
    host.appendChild(tbl);

    host.appendChild(elDiv('vt-verdict', v.verdict));
    if (v.do_not_claim) { host.appendChild(elDiv('vt-warn', v.do_not_claim)); }
  }

  function loadDecision(day) {
    var q = day ? ('?day=' + day) : '';
    return getJSON('/api/decision' + q).then(renderDecision).then(renderLog);
  }

  // ---------- day + status ----------
  function longDate(iso) {
    var d = new Date(iso + 'T00:00:00Z');
    return d.getUTCDate() + ' ' + ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.getUTCMonth()] + ' ' + d.getUTCFullYear();
  }

  function updateStatus(idx) {
    var row = S.summary.daily[idx];
    txt('day-label', longDate(row.date));
    txt('day-count', 'day ' + (idx + 1) + ' of ' + S.summary.dates.length);
    txt('route-date', longDate(row.date));
    var cells = $('strip').children;
    for (var i = 0; i < cells.length; i++) { cells[i].classList.toggle('sel', i === idx); }
  }

  function loadField(idx, qa) {
    var date = S.summary.dates[idx], key = date + '|' + qa;
    if (S.cache.has(key)) { return Promise.resolve(S.cache.get(key)); }
    return getJSON('/api/day/' + date + '?qa=' + qa).then(function (f) { S.cache.set(key, f); return f; });
  }

  var pending = 0;
  function setDay(idx) {
    S.dayIdx = idx; $('day').value = idx;
    updateStatus(idx);
    var my = ++pending;
    loadField(idx, S.qa).then(function (f) {
      if (my !== pending) { return; }
      S.field = f; drawIce(f);
      txt('f-ice', f.source + ' · ' + f.n_known.toLocaleString() + ' cells' +
        (f.qa ? ', ' + f.n_unknown.toLocaleString() + ' marked unknown by QA'
              : ', ' + f.n_exact_zero.toLocaleString() + ' read exactly 0 %'));
      if (S.booted) { loadDecision(S.summary.dates[idx]); }
    }).catch(function (e) { fail(e.message); });
  }

  function setQA(qa) {
    S.qa = qa;
    $('qa-on').classList.toggle('on', qa === 'on');
    $('qa-off').classList.toggle('on', qa === 'off');
    setDay(S.dayIdx);
  }

  // ---------- tooltip: nearest drawn cell ----------
  wrap.addEventListener('mousemove', function (ev) {
    var f = S.field; if (!f) { return; }
    var r = wrap.getBoundingClientRect(), mx = ev.clientX - r.left, my = ev.clientY - r.top;
    var best = -1, bd = 12 * 12, i, p, d;
    for (i = 0; i < f.lat.length; i++) {
      p = px(f.lon[i], f.lat[i]); d = (p[0]-mx)*(p[0]-mx) + (p[1]-my)*(p[1]-my);
      if (d < bd) { bd = d; best = i; }
    }
    var tip = $('tip');
    if (best < 0) { tip.hidden = true; return; }
    tip.hidden = false; tip.style.left = mx + 'px'; tip.style.top = my + 'px';
    tip.textContent = Math.abs(f.lat[best]).toFixed(1) + '°S ' + f.lon[best].toFixed(1) + '°E — ' + f.sic[best] + ' % ice';
  });
  wrap.addEventListener('mouseleave', function () { $('tip').hidden = true; });

  // ---------- boot ----------
  function boot() {
    Promise.all([
      getJSON('/api/summary'),
      getJSON('/api/route'),
      getJSON('/api/protected').catch(function () { return { available: false }; })
    ]).then(function (res) {
      S.summary = res[0]; S.route = res[1]; S.protected = res[2]; B = S.summary.bounds;

      // Say what kind of data this is, before anything else is read.
      var dm = S.summary.data_mode;
      if (dm) {
        txt('mode-text', dm.mode + ' · ' + dm.window);
        $('mode-badge').title = dm.means + ' ' + dm.live_capable;
      }

      var sm = S.summary.summary['Bharati'], ap = S.summary.summary['Bharati approach (100 km N)'];
      txt('t-closed', sm.days_closed); txt('t-obs', sm.days_observed);
      txt('t-pct', sm.pct_days_closed.toFixed(1) + ' %'); txt('t-app', ap.days_closed);

      txt('r-days', S.route.total_traveltime_days.toFixed(2) + ' days');
      txt('r-max', S.route.max_sic_pct_along_route === null ? '—' : S.route.max_sic_pct_along_route.toFixed(0) + ' % ice');
      txt('r-limit', S.summary.ice_limit_pct + ' % ice');
      txt('r-straight', S.route.straight_max_sic_pct === null ? '—' : S.route.straight_max_sic_pct.toFixed(0) + ' % ice — blocked');
      txt('r-legs', S.route.n_legs);
      txt('route-engine', S.route.engine);
      txt('f-route', S.summary.sources.route);

      var strip = $('strip');
      S.summary.daily.forEach(function (row, i) {
        var d = document.createElement('div');
        d.className = 'd ' + (row['Bharati'].passable ? 'open' : 'closed');
        d.title = longDate(row.date) + ' — Bharati ' + (row['Bharati'].passable ? 'open' : 'closed');
        d.addEventListener('click', function () { setDay(i); });
        strip.appendChild(d);
      });
      $('day').max = S.summary.dates.length - 1;
      $('day').addEventListener('input', function (e) { setDay(parseInt(e.target.value, 10)); });
      $('pa-show').addEventListener('change', function (e) {
        S.paShow = e.target.checked; drawVectors();
      });
      $('qa-on').addEventListener('click', function () { setQA('on'); });
      $('qa-off').addEventListener('click', function () { setQA('off'); });
      document.addEventListener('keydown', function (e) {
        if (e.target.tagName === 'INPUT' && e.target.type === 'text') { return; }
        if (e.key === 'ArrowRight') { setDay(Math.min(S.dayIdx + 1, S.summary.dates.length - 1)); }
        if (e.key === 'ArrowLeft')  { setDay(Math.max(S.dayIdx - 1, 0)); }
      });

      $('approve-btn').addEventListener('click', function () {
        var who = $('approver').value.trim();
        var st = $('approve-state');
        if (!who) {
          st.textContent = 'Enter a name and rank. An approval nobody signed is not an approval.';
          st.className = 'approve-state err';
          $('approver').focus();
          return;
        }
        postJSON('/api/decision/approve',
               { by: who, note: '', day: S.summary.dates[S.dayIdx] })
          .then(function (dec) { renderDecision(dec); return renderLog(); })
          .catch(function (e) {
            st.textContent = 'Approval refused: ' + e.message;
            st.className = 'approve-state err';
          });
      });

      var R = S.summary.results;
      R.claims.forEach(function (c) { var li = document.createElement('li'); li.textContent = c; $('claims').appendChild(li); });
      R.do_not_claim.forEach(function (c) { var li = document.createElement('li'); li.textContent = c; $('noclaims').appendChild(li); });
      txt('claims-src', 'Source: ' + R.source);

      sizeCanvas(); drawVectors(); setDay(0);

      S.booted = true;
      return loadDecision(S.summary.dates[0]).then(function () {
        return getJSON('/api/alternatives')
          .then(function (a) { txt('alt-src', a.router + ' · solved on ' + a.date + ' ice'); })
          .catch(function () { txt('alt-src', 'run isih/alternatives.py to compute these'); })
          .then(function () {
            return getJSON('/api/vessel-comparison').then(renderVesselTest).catch(function () {
              txt('vessel-test', 'Run isih/alternatives.py to compute the two-ship test.');
            });
          });
      });
    }).then(function () {
      // warm every day in both modes so the slider never waits on the network
      var q = [];
      S.summary.dates.forEach(function (_, i) { q.push([i, 'on']); q.push([i, 'off']); });
      (function next() { var j = q.shift(); if (!j) { return; } loadField(j[0], j[1]).then(next, next); })();
    }).catch(function (e) { fail(e.message); });
  }

  new ResizeObserver(function () { sizeCanvas(); drawVectors(); drawIce(S.field); }).observe(wrap);
  boot();
})();
