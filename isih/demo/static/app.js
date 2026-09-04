/* ISIH demo — plain JS, no libraries, no network beyond this server.
   Canvas draws the satellite ice raster; SVG draws the route and stations.
   Both share one lat/lon projection so they cannot drift apart. */
(function () {
  'use strict';

  var S = { summary: null, route: null, dayIdx: 0, qa: 'on', cache: new Map(), field: null };
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

  // ---------- projection ----------
  var B; // bounds from the API
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
    // one drawn square per 1-in-2 grid cell; ~0.45° of latitude apart
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
  function drawVectors() {
    while (svg.firstChild) { svg.removeChild(svg.firstChild); }
    if (!S.route || !S.summary) { return; }
    var st = {}; S.summary.stations.forEach(function (s) { st[s.role] = s; });
    var a = px(st.start.lon, st.start.lat), b = px(st.destination.lon, st.destination.lat);

    // straight line — why routing is needed at all, not a competing method
    svg.appendChild(el('line', { x1: a[0], y1: a[1], x2: b[0], y2: b[1],
      stroke: '#C97B1E', 'stroke-width': 1.6, 'stroke-dasharray': '6 5', opacity: 0.9 }));

    // the computed route
    var d = S.route.coords.map(function (c, i) { var p = px(c[0], c[1]); return (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1); }).join(' ');
    svg.appendChild(el('path', { d: d, fill: 'none', stroke: '#FFFFFF', 'stroke-width': 5.5, 'stroke-linejoin': 'round', opacity: 0.85 }));
    svg.appendChild(el('path', { d: d, fill: 'none', stroke: '#0E7A4A', 'stroke-width': 3, 'stroke-linejoin': 'round' }));

    // stations
    function marker(s, dy, anchor) {
      var p = px(s.lon, s.lat);
      var hollow = s.role === 'approach';
      svg.appendChild(el('circle', { cx: p[0], cy: p[1], r: hollow ? 4.5 : 6, fill: hollow ? '#FFFFFF' : '#12303D', stroke: hollow ? '#4A6472' : '#FFFFFF', 'stroke-width': 2 }));
      var label = s.name.toUpperCase().replace(' (100 KM N)', '');
      var t = el('text', { x: p[0] + (anchor === 'end' ? -10 : 10), y: p[1] + dy, 'text-anchor': anchor, 'font-size': hollow ? 10 : 12, 'font-weight': hollow ? 500 : 700, fill: '#12303D', 'paint-order': 'stroke', stroke: '#FFFFFF', 'stroke-width': 3 }, label);
      svg.appendChild(t);
    }
    marker(st.start, 4, 'start');
    marker(st.destination, 4, 'end');
    marker(st.approach, -8, 'end');
  }

  // ---------- day + status ----------
  function longDate(iso) {
    var d = new Date(iso + 'T00:00:00Z');
    return d.getUTCDate() + ' ' + ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.getUTCMonth()] + ' ' + d.getUTCFullYear();
  }
  function pct(v) { return (v === null || v === undefined) ? '—' : v.toFixed(1) + ' %'; }

  function updateStatus(idx) {
    var row = S.summary.daily[idx];
    var b = row['Bharati'], a = row['Bharati approach (100 km N)'];
    $('day-label').textContent = longDate(row.date);
    $('day-n').textContent = 'day ' + (idx + 1) + ' of ' + S.summary.dates.length;
    $('map-date').textContent = longDate(row.date);

    $('b-badge').textContent = b.passable ? 'open' : 'closed';
    $('b-badge').className = 'st-badge ' + (b.passable ? 'open' : 'closed');
    $('b-on').textContent = pct(b.sic_qa_on);
    $('b-off').textContent = pct(b.sic_qa_off);
    $('a-badge').textContent = a.passable ? 'open' : 'closed';
    $('a-badge').className = 'st-badge ' + (a.passable ? 'open' : 'closed');
    $('a-on').textContent = pct(a.sic_qa_on);

    var cells = $('strip').children;
    for (var i = 0; i < cells.length; i++) { cells[i].classList.toggle('today', i === idx); }
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
      if (my !== pending) { return; }          // a newer slider tick won
      S.field = f; drawIce(f);
      $('map-source').textContent = f.source + ' · ' + f.n_known.toLocaleString() + ' cells' +
        (f.qa ? ', ' + f.n_unknown.toLocaleString() + ' marked unknown by QA' : ', ' + f.n_exact_zero.toLocaleString() + ' read exactly 0 %');
    }).catch(function (e) { fail(e.message); });
  }

  function setQA(qa) {
    S.qa = qa;
    $('qa-on').classList.toggle('on', qa === 'on');  $('qa-on').setAttribute('aria-checked', qa === 'on');
    $('qa-off').classList.toggle('on', qa === 'off'); $('qa-off').setAttribute('aria-checked', qa === 'off');
    var note = $('qa-note'), strong = document.createElement('b');
    note.textContent = '';
    if (qa === 'on') {
      note.appendChild(document.createTextNode('Quality-checked: cells the product’s own QA flag marks as land-spillover or no-input are shown as '));
      strong.textContent = 'unknown';
      note.appendChild(strong);
      note.appendChild(document.createTextNode(', not as a value.'));
    } else {
      note.appendChild(document.createTextNode('Raw: what an unguarded reader sees. The same suppressed coastal cells come back as '));
      strong.textContent = '0.0 % — open water';
      note.appendChild(strong);
      note.appendChild(document.createTextNode('. At Bharati on 1 Dec 2019 that is 0.0 % raw against 30.7 % quality-checked.'));
    }
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
    Promise.all([getJSON('/api/summary'), getJSON('/api/route')]).then(function (res) {
      S.summary = res[0]; S.route = res[1]; B = S.summary.bounds;

      var sm = S.summary.summary['Bharati'], ap = S.summary.summary['Bharati approach (100 km N)'];
      $('t-closed').textContent = sm.days_closed; $('t-obs').textContent = sm.days_observed;
      $('t-pct').textContent = sm.pct_days_closed.toFixed(1) + ' %'; $('t-app').textContent = ap.days_closed;
      $('limit').textContent = S.summary.ice_limit_pct;

      $('r-days').textContent = S.route.total_traveltime_days.toFixed(2) + ' days';
      $('r-max').textContent = (S.route.max_sic_pct_along_route === null ? '—' : S.route.max_sic_pct_along_route.toFixed(0) + ' % ice');
      $('r-limit').textContent = S.summary.ice_limit_pct + ' % ice';
      $('r-straight').textContent = (S.route.straight_max_sic_pct === null ? '—' : S.route.straight_max_sic_pct.toFixed(0) + ' % ice — blocked');
      $('r-legs').textContent = S.route.n_legs;
      $('route-engine').textContent = S.route.engine; $('route-date').textContent = longDate(S.route.ice_date);
      $('f-ice').textContent = S.summary.sources.ice; $('f-route').textContent = S.summary.sources.route;

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
      $('qa-on').addEventListener('click', function () { setQA('on'); });
      $('qa-off').addEventListener('click', function () { setQA('off'); });
      document.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowRight') { setDay(Math.min(S.dayIdx + 1, S.summary.dates.length - 1)); }
        if (e.key === 'ArrowLeft')  { setDay(Math.max(S.dayIdx - 1, 0)); }
      });

      var R = S.summary.results;
      R.claims.forEach(function (c) { var li = document.createElement('li'); li.textContent = c; $('claims').appendChild(li); });
      R.do_not_claim.forEach(function (c) { var li = document.createElement('li'); li.textContent = c; $('noclaims').appendChild(li); });
      $('claims-src').textContent = 'Source: ' + R.source;

      sizeCanvas(); drawVectors(); setDay(0);

      // warm every day in both modes so the slider never waits on the network
      var q = [];
      S.summary.dates.forEach(function (_, i) { q.push([i, 'on']); q.push([i, 'off']); });
      (function next() { var j = q.shift(); if (!j) { return; } loadField(j[0], j[1]).then(next, next); })();
    }).catch(function (e) { fail(e.message); });
  }

  new ResizeObserver(function () { sizeCanvas(); drawVectors(); drawIce(S.field); }).observe(wrap);
  boot();
})();
