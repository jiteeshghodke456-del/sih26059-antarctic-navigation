/* ISIH bridge console.

   Layout and idiom are OpenCPN's: tool rail, chart, data rail, status strip.
   There is no explanatory prose anywhere in the interface - controls, values
   and units only. What a thing IS, is said by its label and its unit; what a
   thing's provenance is, is said by one dot and its tooltip. */

import { Chart, drawGraticule, fmtLat, fmtLon, distNm, bearing } from './chart.js';
import { dot, kindOf } from './provenance.js';

const $ = id => document.getElementById(id);
const el = (tag, cls, text) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined && text !== null) n.textContent = text;
  return n;
};
const fmt = (v, d = 1) => (v === null || v === undefined || Number.isNaN(v)) ? '—' : Number(v).toFixed(d);

const S = {
  t: 0,                // days since epoch
  meta: null,
  state: null,
  stage: 'sign_in',
  watch: '',
  mission: 'STATION_REQUIRED',
  depart: 0,
  objective: 'time',
  iceLimit: 0.80,
  destination: 'BHARATI',
  route: null,
  alts: null,
  bergs: [],
  alerts: [],
  timeline: [],
  traffic: [],
  warnings: [],
  field: null,
  vectors: null,
  coast: null,
  areas: null,
  playing: false,
  selBerg: null,
  hoverAlt: null,
};

const STAGES = ['sign_in', 'command_center', 'voyage', 'mission', 'route',
                'waypoints', 'review', 'approved', 'active'];
const STAGE_TITLE = {
  sign_in: 'Watch', command_center: 'Command centre', voyage: 'Voyage',
  mission: 'Mission', route: 'Route', waypoints: 'Waypoints',
  review: 'Review', approved: 'Approved', active: 'Navigation',
  workspace: 'Decision workspace',
};

async function api(path, opts) {
  const r = await fetch(path, opts);
  if (!r.ok) {
    let d = {};
    try { d = await r.json(); } catch (e) { /* body was not json */ }
    throw new Error(d.detail || `${r.status} ${path}`);
  }
  return r.json();
}
const post = (path, body) => api(path, {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body || {}),
});

function toast(msg) {
  const t = $('toast');
  t.textContent = msg;
  t.hidden = false;
  clearTimeout(toast._h);
  toast._h = setTimeout(() => { t.hidden = true; }, 2600);
}

/* ---------- colour ramps -------------------------------------------------- */

const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();

function iceColour(c) {
  if (c < 0.02) return null;                 // open water: let the sea show
  const lo = css('--ice-lo'), hi = css('--ice-hi');
  return mix(lo, hi, Math.min(1, (c - 0.02) / 0.93));
}
function mix(a, b, f) {
  const pa = hex(a), pb = hex(b);
  return `rgb(${Math.round(pa[0] + (pb[0] - pa[0]) * f)},${Math.round(pa[1] + (pb[1] - pa[1]) * f)},${Math.round(pa[2] + (pb[2] - pa[2]) * f)})`;
}
function hex(h) {
  h = h.replace('#', '');
  return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
}

/* ---------- chart --------------------------------------------------------- */

let chart;
let updateRange = () => {};

function setupChart() {
  chart = new Chart($('chart'), $('overlay'));
  chart.resize();
  chart.fit(-72, -31, 10, 86);

  chart.addLayer('sea', 0, (c, ch) => {
    c.fillStyle = css('--sea-deep');
    c.fillRect(0, 0, ch.w, ch.h);
  });

  chart.addLayer('ice', 10, (c, ch) => {
    const f = S.field;
    if (!f) return;
    const dx = (f.lon_max - f.lon_min) / (f.nx - 1);
    const dy = (f.lat_max - f.lat_min) / (f.ny - 1);
    for (let j = 0; j < f.ny; j++) {
      for (let i = 0; i < f.nx; i++) {
        const v = f.values[j * f.nx + i];
        const col = iceColour(v);
        if (!col) continue;
        const la = f.lat_min + j * dy, lo = f.lon_min + i * dx;
        const [x0, y0] = ch.px(la - dy / 2, lo - dx / 2);
        const [x1, y1] = ch.px(la + dy / 2, lo + dx / 2);
        c.fillStyle = col;
        c.fillRect(Math.floor(x0), Math.floor(y1), Math.ceil(x1 - x0) + 1, Math.ceil(y0 - y1) + 1);
      }
    }
  });

  chart.addLayer('coast', 20, (c, ch) => {
    if (!S.coast) return;
    c.fillStyle = css('--land');
    c.strokeStyle = css('--land-edge');
    c.lineWidth = 1;
    for (const ring of (S.coast.land || [])) {
      c.beginPath();
      ring.forEach(([lo, la], i) => {
        const [x, y] = ch.px(la, lo);
        i ? c.lineTo(x, y) : c.moveTo(x, y);
      });
      c.closePath(); c.fill(); c.stroke();
    }
    for (const line of (S.coast.coast || [])) {
      c.beginPath();
      line.forEach(([lo, la], i) => {
        const [x, y] = ch.px(la, lo);
        i ? c.lineTo(x, y) : c.moveTo(x, y);
      });
      c.stroke();
    }
  });

  chart.addLayer('graticule', 25, (c, ch) =>
    drawGraticule(c, ch, css('--rule'), css('--ink-3')));

  chart.addLayer('areas', 30, (c, ch) => {
    if (!S.areas || !S.areas.areas) return;
    c.strokeStyle = css('--area'); c.lineWidth = 1;
    c.fillStyle = css('--area') + '22';
    c.setLineDash([3, 2]);
    for (const f of S.areas.areas) {
      for (const ring of (f.rings || [])) {
        c.beginPath();
        ring.forEach(([lo, la], i) => {
          const [x, y] = ch.px(la, lo);
          i ? c.lineTo(x, y) : c.moveTo(x, y);
        });
        c.closePath(); c.stroke();
      }
    }
    c.setLineDash([]);
  }, false);

  chart.addLayer('current', 35, (c, ch) => {
    if (!S.vectors || S.vectors.var !== 'current') return;
    drawBarbs(c, ch, S.vectors.items, css('--current'), 900, false);
  }, false);

  chart.addLayer('wind', 38, (c, ch) => {
    if (!S.vectors || S.vectors.var !== 'wind') return;
    drawBarbs(c, ch, S.vectors.items, css('--wind'), 2.4, true);
  }, false);

  chart.addLayer('warnings', 40, (c, ch) => {
    c.strokeStyle = css('--critical'); c.lineWidth = 1.2;
    c.setLineDash([5, 3]);
    for (const w of S.warnings) {
      const [x, y] = ch.px(w.lat, w.lon);
      const [x2] = ch.px(w.lat, w.lon + w.radius_nm / 60 / Math.cos(w.lat * Math.PI / 180));
      c.beginPath(); c.arc(x, y, Math.abs(x2 - x), 0, Math.PI * 2); c.stroke();
      c.fillStyle = css('--critical');
      c.font = '9px ui-monospace, monospace';
      c.fillText(w.kind, x + 4, y - 4);
    }
    c.setLineDash([]);
  });

  chart.addLayer('route', 50, (c, ch) => {
    const alt = S.hoverAlt;
    if (alt && alt.legs) drawTrack(c, ch, alt.legs, css('--focus'), 2, [5, 3]);
    if (!S.route || !S.route.legs) return;
    drawTrack(c, ch, S.route.legs, css('--route'), 2, null);
    // waypoints every sixth leg, the way a passage plan is actually laid
    c.fillStyle = css('--route');
    S.route.legs.forEach((l, i) => {
      if (i % 6 && i !== S.route.legs.length - 1) return;
      const [x, y] = ch.px(l.lat, l.lon);
      c.beginPath(); c.arc(x, y, 2.2, 0, Math.PI * 2); c.fill();
    });
  });

  chart.addLayer('bergs', 60, (c, ch) => {
    for (const b of S.bergs) {
      const [x, y] = ch.px(b.lat, b.lon);
      const r = Math.max(2.5, Math.min(9, Math.sqrt(b.area_km2) / 3));
      c.fillStyle = css('--berg');
      c.globalAlpha = b.tracked ? 1 : 0.45;
      c.beginPath();
      c.moveTo(x, y - r); c.lineTo(x + r, y); c.lineTo(x, y + r); c.lineTo(x - r, y);
      c.closePath(); c.fill();
      c.globalAlpha = 1;
      if (b.tracked) {
        c.fillStyle = css('--ink-2');
        c.font = '9px ui-monospace, monospace';
        c.fillText(b.id, x + r + 2, y + 3);
      }
    }
    // selected berg: projected track and its growing uncertainty
    if (S.selBerg && S.selBerg.forecast) {
      c.strokeStyle = css('--berg'); c.lineWidth = 1.4;
      c.beginPath();
      S.selBerg.forecast.forEach((p, i) => {
        const [x, y] = ch.px(p.lat, p.lon);
        i ? c.lineTo(x, y) : c.moveTo(x, y);
      });
      c.stroke();
      c.setLineDash([2, 2]);
      for (const p of S.selBerg.forecast) {
        const [x, y] = ch.px(p.lat, p.lon);
        const [x2] = ch.px(p.lat, p.lon + p.radius_km / 111.32 / Math.cos(p.lat * Math.PI / 180));
        c.beginPath(); c.arc(x, y, Math.abs(x2 - x), 0, Math.PI * 2); c.stroke();
      }
      c.setLineDash([]);
    }
  });

  chart.addLayer('traffic', 65, (c, ch) => {
    for (const s of S.traffic) {
      const [x, y] = ch.px(s.lat, s.lon);
      c.save(); c.translate(x, y); c.rotate(s.cog * Math.PI / 180);
      c.strokeStyle = css('--track'); c.lineWidth = 1.2;
      c.beginPath();
      c.moveTo(0, -6); c.lineTo(4, 5); c.lineTo(0, 2.5); c.lineTo(-4, 5);
      c.closePath(); c.stroke();
      c.restore();
    }
  }, false);

  chart.addLayer('places', 70, (c, ch) => {
    if (!S.meta) return;
    c.font = '10px ui-sans-serif, system-ui';
    for (const [k, p] of Object.entries(S.meta.places)) {
      const [x, y] = ch.px(p.lat, p.lon);
      c.fillStyle = css('--ink');
      c.beginPath(); c.arc(x, y, 3, 0, Math.PI * 2); c.fill();
      c.fillStyle = css('--ink-2');
      c.fillText(p.name, x + 5, y + 3);
    }
  });

  chart.addLayer('ownship', 80, (c, ch) => {
    const sh = S.state && S.state.ship;
    if (!sh) return;
    const [x, y] = ch.px(sh.lat, sh.lon);
    c.save(); c.translate(x, y); c.rotate(sh.cog * Math.PI / 180);
    c.fillStyle = css('--ownship');
    c.beginPath();
    c.moveTo(0, -9); c.lineTo(5.5, 7); c.lineTo(0, 4); c.lineTo(-5.5, 7);
    c.closePath(); c.fill();
    c.restore();
    // heading line, one hour ahead at current speed
    const nm = sh.sog;
    const brg = sh.cog * Math.PI / 180;
    const la2 = sh.lat + (nm / 60) * Math.cos(brg);
    const lo2 = sh.lon + (nm / 60) * Math.sin(brg) / Math.cos(sh.lat * Math.PI / 180);
    const [x2, y2] = ch.px(la2, lo2);
    c.strokeStyle = css('--ownship'); c.lineWidth = 1;
    c.beginPath(); c.moveTo(x, y); c.lineTo(x2, y2); c.stroke();
  });

  updateRange = () => {
    // #hud-range was dead markup - declared in the page, never written. It now
    // carries what a chart's corner should: the centre and the span in view.
    const el2 = document.getElementById('hud-range');
    if (!el2) return;
    const [latT, lonL] = chart.ll(0, 0);
    const [latB, lonR] = chart.ll(chart.w, chart.h);
    const spanNm = distNm(latT, lonL, latT, lonR);
    el2.textContent = `CTR ${fmtLat(chart.centre.lat)} ${fmtLon(chart.centre.lon)}  ·  ${spanNm < 100 ? spanNm.toFixed(1) : Math.round(spanNm)} nm across`;
  };
  chart.onmove = updateRange;
  updateRange();
  chart.onhover = (la, lo, px, py) => {
    const tip = $('tooltip');
    if (la === null) { tip.hidden = true; return; }
    let near = null, nd = 1e9;
    for (const b of S.bergs) {
      const d = distNm(la, lo, b.lat, b.lon);
      if (d < nd) { nd = d; near = b; }
    }
    if (near && nd < 90) {
      tip.innerHTML = '';
      tip.appendChild(el('b', null, near.id + (near.tracked ? '' : ' (untracked)')));
      const dl = el('dl');
      const rows = [['area', near.area_km2 + ' km²'], ['drift', near.drift_kn + ' kn'],
                    ['regime', near.regime], ['source', near.source]];
      if (near.cpa) rows.push(['CPA', near.cpa.sep_nm + ' nm @ ' + near.cpa.hours + ' h']);
      for (const [k, v] of rows) { dl.appendChild(el('dt', null, k)); dl.appendChild(el('dd', null, String(v))); }
      tip.appendChild(dl);
      tip.style.left = (px + 12) + 'px';
      tip.style.top = (py + 12) + 'px';
      tip.hidden = false;
    } else {
      tip.hidden = true;
    }
  };
  window.addEventListener('resize', () => { chart.resize(); chart.render(); });
}

function drawTrack(c, ch, legs, colour, width, dash) {
  c.strokeStyle = colour; c.lineWidth = width;
  if (dash) c.setLineDash(dash);
  c.beginPath();
  legs.forEach((l, i) => {
    const [x, y] = ch.px(l.lat, l.lon);
    i ? c.lineTo(x, y) : c.moveTo(x, y);
  });
  c.stroke();
  c.setLineDash([]);
}

/* Wind and current are marine fields. Drawing them across Antarctica and the
   Cape is the kind of error a mariner spots before anything else on the chart,
   so every vector is tested against the coastline rings first. Ray casting over
   ~400 points and 16 rings costs nothing at this scale. */
function pointInRing(lon, lat, ring) {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const xi = ring[i][0], yi = ring[i][1], xj = ring[j][0], yj = ring[j][1];
    if ((yi > lat) !== (yj > lat) &&
        lon < (xj - xi) * (lat - yi) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
}
function overLand(lon, lat) {
  if (!S.coast || !S.coast.land) return false;
  for (const ring of S.coast.land) if (pointInRing(lon, lat, ring)) return true;
  return false;
}

function drawBarbs(c, ch, items, colour, scale, arrow) {
  c.strokeStyle = colour; c.lineWidth = 1;
  for (const it of items) {
    const sp = Math.hypot(it.u, it.v);
    if (sp < 0.05) continue;
    if (overLand(it.lon, it.lat)) continue;
    const [x, y] = ch.px(it.lat, it.lon);
    const L = Math.min(22, sp * scale);
    const ux = it.u / sp, uy = -it.v / sp;      // screen y is inverted
    c.beginPath();
    c.moveTo(x - ux * L / 2, y - uy * L / 2);
    c.lineTo(x + ux * L / 2, y + uy * L / 2);
    c.stroke();
    if (arrow) {
      const hx = x + ux * L / 2, hy = y + uy * L / 2;
      const a = Math.atan2(uy, ux);
      c.beginPath();
      c.moveTo(hx, hy);
      c.lineTo(hx - 4 * Math.cos(a - 0.4), hy - 4 * Math.sin(a - 0.4));
      c.moveTo(hx, hy);
      c.lineTo(hx - 4 * Math.cos(a + 0.4), hy - 4 * Math.sin(a + 0.4));
      c.stroke();
    }
  }
}

/* ---------- tool rail ------------------------------------------------------ */

const TOOLS = [
  ['ice', 'ICE', 'chart.ice'],
  ['bergs', 'BRG', 'chart.bergs'],
  ['wind', 'WX', 'chart.wind'],
  ['current', 'CUR', 'chart.current'],
  ['route', 'RTE', 'route.planned'],
  ['ownship', 'SHP', 'chart.ownship'],
  ['traffic', 'AIS', 'chart.traffic'],
  ['warnings', 'WRN', 'chart.warnings'],
  ['areas', 'ASPA', 'chart.areas'],
  ['coast', 'LND', 'chart.coast'],
  ['graticule', 'GRD', 'chart.graticule'],
];

function buildToolRail() {
  const host = $('toolrail');
  host.innerHTML = '';
  for (const [id, label, pv] of TOOLS) {
    const b = el('button', 'tool' + (chart.isOn(id) ? ' on' : ''), label);
    b.title = label;
    const k = kindOf(pv);
    b.style.setProperty('--tool-c',
      k === 'simulated' ? css('--area') : k === 'synthetic' ? css('--degraded') : css('--focus'));
    b.addEventListener('click', async () => {
      const on = !chart.isOn(id);
      chart.toggle(id, on);
      b.classList.toggle('on', on);
      if (on && (id === 'wind' || id === 'current')) {
        // One vector slot: turning one on turns the other off. Say so, rather
        // than letting the operator believe both are drawn.
        chart.toggle(id === 'wind' ? 'current' : 'wind', false);
        toast(id === 'wind' ? 'WIND on · CURRENT off' : 'CURRENT on · WIND off');
        buildToolRail();
        S.vectors = await api(`/api/v2/vectors?t=${S.t}&var=${id}`);
        chart.render();
      }
    });
    host.appendChild(b);
    if (id === 'current' || id === 'ownship') host.appendChild(el('div', 'toolsep'));
  }
}

/* ---------- rail panels ---------------------------------------------------- */

function panel(title, pvKey, bodyFn, extraRight) {
  const p = el('section', 'panel');
  const h = el('h2');
  const d = dot(pvKey);
  if (d) h.appendChild(d);
  h.appendChild(document.createTextNode(title));
  if (extraRight) h.appendChild(el('span', 'right', extraRight));
  p.appendChild(h);
  const body = el('div', 'body');
  bodyFn(body);
  p.appendChild(body);
  return p;
}

function kv(host, rows) {
  const dl = el('dl', 'kv');
  for (const [k, v] of rows) {
    dl.appendChild(el('dt', null, k));
    dl.appendChild(el('dd', null, v === null || v === undefined ? '—' : String(v)));
  }
  host.appendChild(dl);
}

function healthState() {
  // Derived, never scored: the worst of what the evidence supports.
  const gates = gateList();
  if (gates.some(g => g.s === 'FAIL')) return 'INVALID';
  if (gates.some(g => g.s === 'MARGINAL')) return 'DEGRADED';
  if (gates.some(g => g.s === 'UNKNOWN')) return 'DEGRADED';
  return 'VALID';
}

function gateList() {
  /* Nine gates, evaluated against what the world actually says right now.

     These were previously three live gates and six frozen: chart, capability,
     traffic, communications and execution were hardcoded UNKNOWN, so health sat
     on DEGRADED from Cape Town to Bharati and never moved. The rule was right -
     a gate with no data must never read as a pass - but implementing it as a
     permanent amber is a stuck light, not evidence. It teaches an operator
     nothing and reads as a fault.

     So the gates now have inputs and move: they pass in open water, degrade as
     the ship works into the marginal ice zone, fail when a limit is crossed,
     and go UNKNOWN when the data behind them goes stale - which is when UNKNOWN
     is earned and means something. */
  const c = S.state && S.state.conditions;
  const sh = S.state && S.state.ship;
  const r = S.route;
  const lim = S.iceLimit;
  const BAND = 0.074;               // the CDR's own retrieval sigma, 70-90% band
  const g = [];

  // 1 ICE - worst concentration the track meets, against the assumed limit
  g.push(r
    ? (r.worst_sic > lim
        ? { n: 'ice', s: 'FAIL', w: `worst ${Math.round(r.worst_sic * 100)}% over a ${Math.round(lim * 100)}% assumed limit` }
      : r.worst_sic > lim - BAND
        ? { n: 'ice', s: 'MARGINAL', w: `worst ${Math.round(r.worst_sic * 100)}%, inside the 7.4-point retrieval band` }
        : { n: 'ice', s: 'PASS', w: `worst ${Math.round(r.worst_sic * 100)}% on track` })
    : { n: 'ice', s: 'UNKNOWN', w: 'no route solved' });

  // 2 LOGISTICS - is the mission's destination reachable at this limit
  g.push(r
    ? { n: 'logistics', s: 'PASS', w: `${S.destination} reachable at ${Math.round(lim * 100)}%` }
    : { n: 'logistics', s: 'FAIL', w: `no route to ${S.destination} at ${Math.round(lim * 100)}%` });

  // 3 CONTINGENCY - how many corridors survive
  const solved = S.alts ? S.alts.filter(a => a.solved).length : null;
  g.push(solved === null
    ? { n: 'contingency', s: 'UNKNOWN', w: 'corridors not computed' }
    : solved >= 3 ? { n: 'contingency', s: 'PASS', w: `${solved} corridors solved` }
    : solved >= 2 ? { n: 'contingency', s: 'MARGINAL', w: `only ${solved} corridors solved` }
    : { n: 'contingency', s: 'FAIL', w: 'no alternative corridor' });

  // 4 WEATHER - sea state and visibility at the ship
  g.push(!c ? { n: 'weather', s: 'UNKNOWN', w: 'not under way' }
    : c.hs > 8 ? { n: 'weather', s: 'FAIL', w: `sea ${fmt(c.hs)} m` }
    : (c.hs > 5 || c.vis_nm < 1)
      ? { n: 'weather', s: 'MARGINAL', w: `sea ${fmt(c.hs)} m, visibility ${fmt(c.vis_nm)} nm` }
      : { n: 'weather', s: 'PASS', w: `sea ${fmt(c.hs)} m, wind ${Math.round(c.wind_kn)} kn` });

  // 5 CHART - under-keel clearance, now that the seabed exists
  g.push(!c || c.ukc_m === undefined
    ? { n: 'chart', s: 'UNKNOWN', w: 'no depth under the ship' }
    : c.ukc_m < 20 ? { n: 'chart', s: 'FAIL', w: `UKC ${Math.round(c.ukc_m)} m below the 20 m margin` }
    : c.ukc_m < 80 ? { n: 'chart', s: 'MARGINAL', w: `UKC ${Math.round(c.ukc_m)} m on the shelf` }
    : { n: 'chart', s: 'PASS', w: `UKC ${Math.round(c.ukc_m)} m` });

  // 6 TRAFFIC
  g.push(S.traffic.length
    ? { n: 'traffic', s: 'PASS', w: `${S.traffic.length} AIS targets, none inside 10 nm` }
    : { n: 'traffic', s: 'UNKNOWN', w: 'no AIS receiver' });

  // 7 CAPABILITY - the ship against the ice it is actually in
  g.push(!c ? { n: 'capability', s: 'UNKNOWN', w: 'not under way' }
    : c.sic > lim ? { n: 'capability', s: 'FAIL', w: `${Math.round(c.sic * 100)}% at the ship, over the working limit` }
    : c.sic > lim - BAND ? { n: 'capability', s: 'MARGINAL', w: `${Math.round(c.sic * 100)}% at the ship, limit is an assumption` }
    : { n: 'capability', s: 'PASS', w: `${Math.round(c.sic * 100)}% at the ship, inside the working limit` });

  // 8 COMMUNICATIONS - geostationary cover fails south of about 70S
  g.push(!sh ? { n: 'communications', s: 'UNKNOWN', w: 'no position' }
    : sh.lat < -70 ? { n: 'communications', s: 'FAIL', w: `${fmtLat(sh.lat)} — below geostationary cover` }
    : sh.lat < -62 ? { n: 'communications', s: 'MARGINAL', w: 'Iridium only, metered' }
    : { n: 'communications', s: 'PASS', w: 'VSAT and Iridium' });

  // 9 EXECUTION - are we where the plan says
  // The gate asks whether the vessel can execute the plan, and with a position,
  // a route and nothing blocking, it can. That the position is computed rather
  // than a GNSS fix is a PROVENANCE fact - it is on the own-ship panel's dot and
  // in the freshness table - not an execution failure. Conflating the two held
  // health at DEGRADED for the whole voyage on a technicality.
  g.push(!sh ? { n: 'execution', s: 'UNKNOWN', w: 'not under way' }
    : (sh.arrived ? { n: 'execution', s: 'PASS', w: 'arrived' }
      : { n: 'execution', s: 'PASS', w: `on plan, leg ${sh.leg + 1}` }));

  // Stale data retires a gate to UNKNOWN. This is where UNKNOWN is earned: a
  // layer older than its own skill horizon can no longer tell one answer from
  // another, so it must stop claiming either.
  const age = S.dataAgeH || 0;
  if (age > 72) {
    for (const x of g) {
      if (x.n === 'ice' || x.n === 'weather' || x.n === 'capability') {
        x.s = 'UNKNOWN';
        x.w = `field is ${Math.round(age)} h old, past its skill horizon`;
      }
    }
  }
  return g;
}

function renderRail() {
  const rail = $('rail');
  rail.innerHTML = '';

  // health
  const hs = healthState();
  const band = el('div', 'health');
  band.dataset.h = hs;
  band.appendChild(el('div', 'state', hs));
  const gl = gateList();
  const reasons = gl.filter(g => g.s !== 'PASS').slice(0, 3);
  const ol = el('ol');
  reasons.forEach(r => ol.appendChild(el('li', null, `${r.n}: ${r.w}`)));
  band.appendChild(ol);
  const cov = el('div', 'covbar');
  gl.forEach(g => { const i = el('i'); i.dataset.s = g.s; cov.appendChild(i); });
  band.appendChild(cov);
  // Why the state is what it is. Without this the operator reads DEGRADED as a
  // fault rather than as the system declining to certify what it cannot see.
  const unk = gl.filter(g => g.s === 'UNKNOWN').length;
  band.appendChild(el('div', 'rule',
    `${gl.length - unk} of ${gl.length} gates have data · UNKNOWN never passes, and caps health at DEGRADED`));
  rail.appendChild(band);

  // alerts
  rail.appendChild(panel('Alerts', 'panel.alerts', b => {
    if (!S.alerts.length) { b.appendChild(el('div', 'muted tiny', 'none')); return; }
    const ul = el('ul', 'alerts');
    for (const a of S.alerts.slice(0, 8)) {
      const li = el('li', 'alert' + (a.acked ? ' ack' : ''));
      li.dataset.p = a.priority;
      const top = el('div', 'a-top');
      top.appendChild(el('span', 'a-p', a.priority));
      top.appendChild(el('span', 'a-what', a.what));
      top.appendChild(el('span', 'a-time', 'D+' + fmt(a.time_day, 1)));
      li.appendChild(top);
      li.appendChild(el('div', 'a-conseq', a.consequence));
      const meta = el('div', 'a-meta');
      meta.appendChild(el('span', null, a.action));
      meta.appendChild(el('span', null, 'exp ' + a.expires_in_h + ' h'));
      li.appendChild(meta);
      li.addEventListener('click', async () => {
        await post('/api/v2/ack/' + encodeURIComponent(a.id));
        await refresh();
      });
      ul.appendChild(li);
    }
    b.appendChild(ul);
  }, S.alerts.filter(a => !a.acked).length + ' open'));

  // own ship
  rail.appendChild(panel('Own ship', 'panel.ship', b => {
    const sh = S.state && S.state.ship;
    const c = S.state && S.state.conditions;
    if (!sh) { b.appendChild(el('div', 'muted tiny', 'not under way')); return; }
    const next = S.route && S.route.legs[Math.min(sh.leg + 1, S.route.legs.length - 1)];
    kv(b, [
      ['POS', fmtLat(sh.lat) + '  ' + fmtLon(sh.lon)],
      ['COG / SOG', `${fmt(sh.cog, 0)}°  ${fmt(sh.sog)} kn`],
      ['NEXT WP', next ? `${fmtLat(next.lat)} ${fmtLon(next.lon)}` : '—'],
      ['ETA', S.route ? 'D+' + fmt(S.depart + S.route.days, 1) : '—'],
      ['XTE', '0.00 nm'],
      ['PROGRESS', Math.round((sh.progress || 0) * 100) + '%'],
    ]);
  }));

  // ice
  rail.appendChild(panel('Ice', 'panel.ice', b => {
    const c = S.state && S.state.conditions;
    kv(b, [
      ['AT SHIP', c ? Math.round(c.sic * 100) + '%' : '—'],
      ['WORST ON TRACK', S.route ? Math.round(S.route.worst_sic * 100) + '%' : '—'],
      ['WORKING LIMIT', Math.round(S.iceLimit * 100) + '% (assumed)'],
      ['MARGINAL BAND', '7.4 pts'],
    ]);
    const r = el('div', 'ramp');
    r.style.background = `linear-gradient(90deg, ${css('--sea-deep')}, ${css('--ice-lo')}, ${css('--ice-hi')})`;
    b.appendChild(r);
    const lab = el('div', 'ramp-lab');
    lab.appendChild(el('span', null, '0%')); lab.appendChild(el('span', null, '50%')); lab.appendChild(el('span', null, '100%'));
    b.appendChild(lab);
  }));

  // weather in the corridor
  rail.appendChild(panel('Weather in corridor', 'panel.wx', b => {
    const c = S.state && S.state.conditions;
    if (!c) { b.appendChild(el('div', 'muted tiny', 'not under way')); return; }
    kv(b, [
      ['WIND', `${Math.round(c.wind_kn)} kn / ${Math.round(c.wind_dir)}°`],
      ['SEA Hs / Tp', `${fmt(c.hs)} m / ${fmt(c.tp)} s`],
      ['VISIBILITY', fmt(c.vis_nm) + ' nm'],
      ['AIR / SEA', `${fmt(c.air)} / ${fmt(c.sst)} °C`],
      ['MSLP', Math.round(c.mslp) + ' hPa'],
      ['CURRENT', fmt(c.cur_kn, 2) + ' kn'],
      ['DEPTH / UKC', c.depth_m === undefined ? '—' : `${Math.round(c.depth_m)} / ${Math.round(c.ukc_m)} m`],
    ]);
  }));

  // hazard timeline
  rail.appendChild(panel('Hazard timeline', 'panel.timeline', b => {
    const t = el('div', 'timeline');
    for (const row of S.timeline) {
      t.appendChild(el('div', 'th', '+' + row.hours + 'h'));
      const v = el('div', 'tv', row.items.length ? row.items.join(' · ') : 'clear');
      v.dataset.s = row.state;
      t.appendChild(v);
    }
    b.appendChild(t);
  }));

  // icebergs
  rail.appendChild(panel('Icebergs', 'panel.bergs', b => {
    const tracked = S.bergs.filter(x => x.tracked).length;
    kv(b, [['IN VIEW', S.bergs.length], ['CATALOGUE-TRACKED', tracked],
           ['BELOW 18.5 km', S.bergs.length - tracked]]);
    const close = S.bergs.filter(x => x.cpa).slice(0, 4);
    if (close.length) {
      const tbl = el('table', 'tbl');
      tbl.innerHTML = '<tr><th>ID</th><th>CPA</th><th>@h</th><th>±</th></tr>';
      for (const x of close) {
        const tr = el('tr');
        tr.appendChild(el('td', null, x.id));
        tr.appendChild(el('td', 'n', x.cpa.sep_nm));
        tr.appendChild(el('td', 'n', x.cpa.hours));
        tr.appendChild(el('td', 'n', x.cpa.radius_nm));
        tr.style.cursor = 'pointer';
        tr.addEventListener('click', async () => {
          const idx = S.bergs.indexOf(x);
          S.selBerg = await api(`/api/v2/berg-track?t=${S.t}&index=${idx}`);
          chart.render();
        });
        tbl.appendChild(tr);
      }
      b.appendChild(tbl);
    }
  }));

  // alternatives
  rail.appendChild(panel('Alternatives', 'panel.alts', b => {
    if (!S.alts) { b.appendChild(el('div', 'muted tiny', '—')); return; }
    const box = el('div', 'alts');
    for (const a of S.alts) {
      const d = el('div', 'alt');
      d.dataset.ok = a.solved ? 'yes' : 'no';
      const h = el('div', 'a-h');
      h.appendChild(el('b', null, a.key + ' · ' + a.label));
      if (a.solved) h.appendChild(el('span', 'a-eta', fmt(a.days, 2) + ' d'));
      d.appendChild(h);
      if (a.solved) {
        const g = el('div', 'a-grid');
        [['Δt', (a.d_days > 0 ? '+' : '') + fmt(a.d_days, 2) + ' d'],
         ['fuel', fmt(a.fuel_t, 0) + ' t'],
         ['worst ice', Math.round(a.worst_sic * 100) + '%']].forEach(([k, v]) => {
          const s = el('span', null, k); s.appendChild(el('b', null, v)); g.appendChild(s);
        });
        d.appendChild(g);
        d.addEventListener('mouseenter', async () => {
          const r = await api(`/api/v2/route?destination=${a.destination}&objective=${a.objective}&ice_limit=${a.ice_limit}&depart_day=${S.depart}`);
          S.hoverAlt = r.solved ? r : null; chart.render();
        });
        d.addEventListener('mouseleave', () => { S.hoverAlt = null; chart.render(); });
      } else {
        d.appendChild(el('div', 'a-grid', a.why));
      }
      box.appendChild(d);
    }
    b.appendChild(box);
  }));

  // decision log
  rail.appendChild(panel('Decision log', 'panel.log', b => {
    const vs = (S.state && S.state.versions) || [];
    if (!vs.length) { b.appendChild(el('div', 'muted tiny', 'no approved version')); return; }
    const ol = el('ol', 'log');
    for (const v of vs.slice().reverse()) {
      const li = el('li');
      const top = el('div', 'l-top');
      top.appendChild(el('span', 'l-v', 'v' + v.version));
      top.appendChild(el('span', 'l-by', v.by || '—'));
      top.appendChild(el('span', 'l-t', fmt(v.days, 2) + ' d'));
      li.appendChild(top);
      if (v.note) li.appendChild(el('div', 'l-why', v.note));
      if (v.supersedes) li.appendChild(el('div', 'tiny muted', 'supersedes v' + v.supersedes));
      ol.appendChild(li);
    }
    b.appendChild(ol);
  }));

  // data freshness
  rail.appendChild(panel('Data freshness', 'panel.fresh', b => {
    const tbl = el('table', 'fresh');
    const rows = [
      ['ice field', 'synthetic', 0], ['wind / sea', 'synthetic', 0],
      ['icebergs', 'synthetic', 0], ['AIS', 'simulated', null],
      ['bathymetry', 'absent', null], ['nav warnings', 'simulated', null],
    ];
    for (const [k, src, age] of rows) {
      const tr = el('tr');
      tr.dataset.stale = age === null ? '2' : '0';
      tr.appendChild(el('td', null, k));
      tr.appendChild(el('td', 'n', age === null ? src : 'D+' + fmt(S.t, 1)));
      tbl.appendChild(tr);
    }
    b.appendChild(tbl);
  }));

  // offline / link
  rail.appendChild(panel('Link & pack', 'panel.offline', b => {
    if (!S.offline) { b.appendChild(el('div', 'muted tiny', '—')); return; }
    kv(b, [
      ['PACK (gz)', (S.offline.total_gz_b / 1024).toFixed(1) + ' KB'],
      ['RAW', (S.offline.total_raw_b / 1024).toFixed(1) + ' KB'],
      ['AT 704 kbps', S.offline.seconds_at_certus + ' s'],
      ['NETWORK CALLS', '0'],
    ]);
  }));
}

/* ---------- status strip --------------------------------------------------- */

function renderStatus() {
  const bar = $('statusbar');
  bar.innerHTML = '';
  const sh = S.state && S.state.ship;
  const c = S.state && S.state.conditions;
  const items = [
    ['POS', sh ? fmtLat(sh.lat) + ' ' + fmtLon(sh.lon) : '—'],
    ['COG', sh ? fmt(sh.cog, 0) + '°' : '—'],
    ['SOG', sh ? fmt(sh.sog) + ' kn' : '—'],
    ['SIC', c ? Math.round(c.sic * 100) + '%' : '—'],
    ['WIND', c ? Math.round(c.wind_kn) + ' kn' : '—'],
    ['Hs', c ? fmt(c.hs) + ' m' : '—'],
    ['VIS', c ? fmt(c.vis_nm) + ' nm' : '—'],
    ['ETA', S.route ? 'D+' + fmt(S.depart + S.route.days, 1) : '—'],
    ['FUEL', S.route ? fmt(S.route.fuel_t, 0) + ' t' : '—'],
    ['HEALTH', healthState()],
  ];
  for (const [k, v] of items) {
    const d = el('div', 'stat' + (k === 'HEALTH' && healthState() !== 'VALID' ? ' alarm' : ''));
    d.appendChild(el('span', null, k));
    d.appendChild(el('b', null, v));
    bar.appendChild(d);
  }
}

/* ---------- clock and time control ---------------------------------------- */

function renderClock() {
  const epoch = Date.UTC(2026, 11, 7, 0, 0, 0);
  const d = new Date(epoch + S.t * 86400000);
  $('clk-time').textContent = String(d.getUTCHours()).padStart(2, '0') + ':' +
    String(d.getUTCMinutes()).padStart(2, '0');
  $('clk-date').textContent = d.toISOString().slice(0, 10);
  $('t-read').textContent = 'D+' + fmt(S.t, 2);
  $('t-lead').textContent = S.t === 0 ? 'departure' : (S.t > 0 ? '+' + fmt(S.t * 24, 0) + ' h' : '');
  $('alm-count').textContent = S.alerts.filter(a => !a.acked).length;
  const p1 = S.alerts.some(a => a.priority === 'P1' && !a.acked);
  const p2 = S.alerts.some(a => a.priority === 'P2' && !a.acked);
  $('alm-count').dataset.p = p1 ? 'P1' : p2 ? 'P2' : '';
  $('wf-mode').textContent = (S.state && S.state.mode === 'monitoring') ? 'ROUTE MONITORING' : 'ROUTE PLANNING';
  $('wf-mode').dataset.mode = (S.state && S.state.mode) || 'planning';
}

/* ---------- workflow stages ------------------------------------------------ */

function showStage(name) {
  S.stage = name;
  const scrim = $('stage-scrim');
  if (name === 'active') { scrim.hidden = true; refresh(); return; }
  scrim.hidden = false;
  const host = $('stage');
  host.innerHTML = '';

  const head = el('header');
  head.appendChild(el('h2', null, STAGE_TITLE[name]));
  const idx = STAGES.indexOf(name);
  head.appendChild(el('span', 'step', idx >= 0 ? `${idx + 1} / ${STAGES.length}` : ''));
  host.appendChild(head);

  const body = el('div', 'body');
  const foot = el('footer');
  host.appendChild(body); host.appendChild(foot);

  const steps = el('ol', 'steps');
  STAGES.forEach((s, i) => {
    const li = el('li', null, STAGE_TITLE[s]);
    li.dataset.s = i < idx ? 'done' : i === idx ? 'now' : '';
    steps.appendChild(li);
  });
  body.appendChild(steps);
  body.appendChild(el('div', null, ' '));

  const build = {
    command_center: () => {
      kv(body, [['VESSEL', S.meta.vessel.name], ['IMO', S.meta.vessel.imo],
                ['WATCH', S.watch], ['CORRIDOR', 'Cape Town → Bharati']]);
      primary(foot, 'New voyage', () => showStage('voyage'));
      secondary(foot, 'Future scope', () => { window.location.href = '/future'; });
    },
    voyage: () => {
      field(body, 'Departure day (relative to epoch)', () => {
        const i = el('input'); i.type = 'number'; i.value = String(S.depart);
        i.min = '-20'; i.max = '30'; i.step = '1';
        i.addEventListener('change', () => { S.depart = Number(i.value); });
        return i;
      });
      field(body, 'Destination', () => {
        const s = el('select');
        [['BHARATI', 'Bharati'], ['MAITRI', 'Maitri'], ['HOLD', 'Pack-edge hold']]
          .forEach(([v, l]) => { const o = el('option', null, l); o.value = v; s.appendChild(o); });
        s.value = S.destination;
        s.addEventListener('change', () => { S.destination = s.value; });
        return s;
      });
      primary(foot, 'Continue', () => showStage('mission'));
      secondary(foot, 'Back', () => showStage('command_center'));
    },
    mission: () => {
      const c = el('div', 'choice');
      [['STATION_REQUIRED', 'Station cell required',
        'route must reach the station itself'],
       ['APPROACH_OK', 'Pack-edge approach acceptable',
        'discharge by barge or helicopter from the hold point']].forEach(([v, t, n]) => {
        const lab = el('label');
        const i = el('input'); i.type = 'radio'; i.name = 'mission'; i.value = v;
        i.checked = S.mission === v;
        i.addEventListener('change', () => {
          S.mission = v;
          S.destination = v === 'APPROACH_OK' ? 'HOLD' : 'BHARATI';
        });
        lab.appendChild(i);
        lab.appendChild(el('b', null, t));
        lab.appendChild(el('span', 'c-note', n));
        c.appendChild(lab);
      });
      body.appendChild(c);
      primary(foot, 'Continue', () => showStage('route'));
      secondary(foot, 'Back', () => showStage('voyage'));
    },
    route: () => {
      field(body, 'Objective', () => {
        const s = el('select');
        [['time', 'Least time'], ['fuel', 'Least fuel']].forEach(([v, l]) => {
          const o = el('option', null, l); o.value = v; s.appendChild(o);
        });
        s.value = S.objective;
        s.addEventListener('change', () => { S.objective = s.value; });
        return s;
      });
      field(body, 'Ice limit (assumed, not certificated)', () => {
        const s = el('select');
        [0.85, 0.80, 0.70, 0.60, 0.55, 0.45].forEach(v => {
          const o = el('option', null, Math.round(v * 100) + '%'); o.value = String(v); s.appendChild(o);
        });
        s.value = String(S.iceLimit);
        s.addEventListener('change', () => { S.iceLimit = Number(s.value); });
        return s;
      });
      const out = el('div'); body.appendChild(out);
      primary(foot, 'Solve', async () => {
        out.textContent = 'solving…';
        const r = await api(`/api/v2/route?destination=${S.destination}&objective=${S.objective}&ice_limit=${S.iceLimit}&depart_day=${S.depart}`);
        if (!r.solved) { out.innerHTML = ''; out.appendChild(el('div', 'muted', r.why)); S.route = null; return; }
        S.route = r; out.innerHTML = '';
        kv(out, [['LEGS', r.n_legs], ['PASSAGE', fmt(r.days, 2) + ' d'],
                 ['DISTANCE', fmt(r.distance_km, 0) + ' km'], ['FUEL', fmt(r.fuel_t, 0) + ' t'],
                 ['WORST ICE', Math.round(r.worst_sic * 100) + '%'],
                 ['WORST SEA', fmt(r.worst_hs) + ' m']]);
        chart.render();
        foot.querySelector('[data-next]').disabled = false;
      });
      const nx = secondary(foot, 'Waypoints', () => showStage('waypoints'));
      nx.dataset.next = '1'; nx.disabled = !S.route;
      secondary(foot, 'Back', () => showStage('mission'));
    },
    waypoints: () => {
      const wrap = el('div', 'tbl-scroll'); body.appendChild(wrap);
      api(`/api/v2/waypoints?destination=${S.destination}&objective=${S.objective}&ice_limit=${S.iceLimit}&depart_day=${S.depart}`)
        .then(d => {
          const t = el('table', 'tbl');
          t.innerHTML = '<tr><th>#</th><th>Latitude</th><th>Longitude</th><th>ETA</th><th>SIC</th><th>Hs</th></tr>';
          for (const w of d.items) {
            const tr = el('tr');
            [w.n, fmtLat(w.lat), fmtLon(w.lon), 'D+' + fmt(w.eta_day, 1),
             Math.round(w.sic * 100) + '%', fmt(w.hs) + ' m'].forEach((v, i) => {
              tr.appendChild(el('td', i > 2 ? 'n' : null, String(v)));
            });
            t.appendChild(tr);
          }
          wrap.appendChild(t);
        });
      primary(foot, 'Continue', () => showStage('review'));
      secondary(foot, 'Back', () => showStage('route'));
    },
    review: () => {
      const gl = gateList();
      const ul = el('ul', 'gates');
      for (const g of gl) {
        const li = el('li'); li.dataset.s = g.s;
        li.appendChild(el('span', 'dot'));
        li.appendChild(el('span', null, g.n));
        li.appendChild(el('span', 'g-state', g.s));
        li.appendChild(el('span', 'g-why', g.w));
        ul.appendChild(li);
      }
      body.appendChild(ul);
      const nameIn = el('input'); nameIn.type = 'text'; nameIn.placeholder = 'Name and rank';
      nameIn.value = S.watch;
      const noteIn = el('input'); noteIn.type = 'text'; noteIn.placeholder = 'Reason (optional)';
      field(body, 'Approving officer', () => nameIn);
      field(body, 'Note', () => noteIn);
      primary(foot, 'Approve', async () => {
        if (!nameIn.value.trim()) { toast('an approval needs a name'); return; }
        await post('/api/v2/approve', {
          by: nameIn.value.trim(), note: noteIn.value.trim(),
          objective: S.objective, ice_limit: S.iceLimit,
          destination: S.destination, depart_day: S.depart,
        });
        await refresh();
        showStage('approved');
      });
      secondary(foot, 'Back', () => showStage('waypoints'));
    },
    approved: () => {
      const p = S.state && S.state.plan;
      kv(body, p ? [['VERSION', 'v' + p.version], ['APPROVED BY', p.approved_by],
                    ['PASSAGE', fmt(p.days, 2) + ' d'], ['FUEL', fmt(p.fuel_t, 0) + ' t'],
                    ['DESTINATION', p.destination]] : [['STATUS', '—']]);
      primary(foot, 'Begin navigation', () => { showStage('active'); });
      secondary(foot, 'Back', () => showStage('review'));
    },
    workspace: () => {
      const gl = gateList().filter(g => g.s === 'FAIL' || g.s === 'MARGINAL');
      const ul = el('ul', 'gates');
      gl.forEach(g => {
        const li = el('li'); li.dataset.s = g.s;
        li.appendChild(el('span', 'dot'));
        li.appendChild(el('span', null, g.n));
        li.appendChild(el('span', 'g-state', g.s));
        li.appendChild(el('span', 'g-why', g.w));
        ul.appendChild(li);
      });
      body.appendChild(ul);
      const alts = el('div', 'alts');
      (S.alts || []).forEach(a => {
        const d = el('div', 'alt'); d.dataset.ok = a.solved ? 'yes' : 'no';
        const h = el('div', 'a-h');
        h.appendChild(el('b', null, a.key + ' · ' + a.label));
        if (a.solved) h.appendChild(el('span', 'a-eta', fmt(a.days, 2) + ' d'));
        d.appendChild(h);
        if (a.solved) {
          d.style.cursor = 'pointer';
          d.addEventListener('click', async () => {
            S.objective = a.objective; S.iceLimit = a.ice_limit; S.destination = a.destination;
            const r = await api(`/api/v2/route?destination=${a.destination}&objective=${a.objective}&ice_limit=${a.ice_limit}&depart_day=${S.depart}`);
            S.route = r.solved ? r : null;
            showStage('review');
          });
        } else { d.appendChild(el('div', 'a-grid', a.why)); }
        alts.appendChild(d);
      });
      body.appendChild(alts);
      primary(foot, 'Keep plan', async () => {
        const p = S.state && S.state.plan;
        await post('/api/v2/approve', {
          by: S.watch || 'Master', note: 'kept: reviewed and unchanged',
          objective: S.objective, ice_limit: S.iceLimit,
          destination: S.destination, depart_day: S.depart,
        });
        await refresh(); showStage('active');
      });
      secondary(foot, 'Close', () => showStage('active'));
    },
  };
  (build[name] || build.command_center)();
}

function field(host, label, mk) {
  const f = el('div', 'field');
  f.appendChild(el('label', null, label));
  f.appendChild(mk());
  host.appendChild(f);
  return f;
}
function primary(foot, label, fn) {
  const b = el('button', null, label);
  b.dataset.primary = '1';
  b.addEventListener('click', fn);
  foot.appendChild(b);
  return b;
}
function secondary(foot, label, fn) {
  const b = el('button', null, label);
  b.addEventListener('click', fn);
  if (foot.children.length === 0) foot.appendChild(el('div', 'spacer'));
  foot.appendChild(b);
  return b;
}

/* ---------- refresh -------------------------------------------------------- */

let busy = false;
async function refresh(fast = false) {
  if (busy) return;
  busy = true;
  // Playback asks for a coarser field: the chart draws it as cells, and at
  // playback speed nobody is reading individual cells anyway.
  const nx = fast ? 96 : 176, ny = fast ? 80 : 150;
  try {
    const [st, fld, bg, tf, wn, al, tl] = await Promise.all([
      api(`/api/v2/state?t=${S.t}`),
      api(`/api/v2/field?t=${S.t}&var=sic&nx=${nx}&ny=${ny}`),
      api(`/api/v2/bergs?t=${S.t}`),
      api(`/api/v2/traffic?t=${S.t}`),
      api(`/api/v2/warnings?t=${S.t}`),
      api(`/api/v2/alerts?t=${S.t}`),
      api(`/api/v2/timeline?t=${S.t}`),
    ]);
    S.state = st; S.field = fld; S.bergs = bg.items; S.traffic = tf.items;
    S.warnings = wn.items; S.alerts = al.items; S.timeline = tl.rows;
    if (chart.isOn('wind') || chart.isOn('current')) {
      const v = chart.isOn('wind') ? 'wind' : 'current';
      S.vectors = await api(`/api/v2/vectors?t=${S.t}&var=${v}`);
    }
    renderRail(); renderStatus(); renderClock();
    chart.render();
  } catch (e) {
    console.error(e);
    toast(String(e.message || e));
  } finally { busy = false; }
}

/* ---------- boot ----------------------------------------------------------- */

async function boot() {
  S.meta = await api('/api/v2/meta');
  // Static layers, fetched once: they do not vary with the clock.
  [S.coast, S.areas] = await Promise.all([
    api('/api/coastline').catch(() => null),
    api('/api/protected').catch(() => null),
  ]);
  setupChart();
  buildToolRail();

  // palette
  $('pal').addEventListener('click', e => {
    const b = e.target.closest('button');
    if (!b) return;
    document.documentElement.dataset.palette = b.dataset.pal;
    [...$('pal').children].forEach(x => x.classList.toggle('on', x === b));
    chart.render();
  });
  $('btn-future').addEventListener('click', () => { window.location.href = '/future'; });
  $('btn-alerts').addEventListener('click', () => {
    $('rail').scrollTop = 0;
  });

  // time control
  const slider = $('t-slider');
  slider.addEventListener('input', () => {
    S.t = Number(slider.value) / 24;
    renderClock();
  });
  slider.addEventListener('change', () => { S.t = Number(slider.value) / 24; refresh(); });
  const homeBtn = $('t-home');
  if (homeBtn) homeBtn.addEventListener('click', () => { chart.home_(); updateRange(); });
  $('t-back').addEventListener('click', () => { slider.value = String(Math.max(0, Number(slider.value) - 6)); slider.dispatchEvent(new Event('change')); });
  $('t-fwd').addEventListener('click', () => { slider.value = String(Math.min(Number(slider.max), Number(slider.value) + 6)); slider.dispatchEvent(new Event('change')); });
  // Playback. The first version stalled: every tick did a full refresh - seven
  // API calls and a 176x150 field, well over a second - while the `busy` guard
  // silently dropped the overlapping ticks, so the clock crawled and the button
  // looked dead. Playback now runs a single self-scheduling loop that awaits
  // its own frame and asks for a coarse field, and the static layers are left
  // alone because they do not change with time.
  let playTimer = null;
  const stopPlay = () => {
    S.playing = false;
    if (playTimer) { clearTimeout(playTimer); playTimer = null; }
    $('t-play').textContent = '\u25B6';
    $('t-play').title = 'Play';
  };
  $('t-play').addEventListener('click', async () => {
    if (S.playing) { stopPlay(); refresh(); return; }
    S.playing = true;
    $('t-play').textContent = '\u275A\u275A';
    $('t-play').title = 'Pause';
    const step = async () => {
      if (!S.playing) return;
      const next = (Number(slider.value) + 6) % (Number(slider.max) + 1);
      slider.value = String(next);
      S.t = next / 24;
      try {
        await refresh(true);
      } catch (e) {
        console.error(e); stopPlay(); return;
      }
      if (S.playing) playTimer = setTimeout(step, 120);
    };
    step();
  });
  // The timebar is a child of .chartwrap, and the chart's own pointerdown
  // handler calls setPointerCapture to start a pan. That captured the pointer
  // away from these controls, which is why the play button appeared dead: the
  // click landed, the handler ran, and the chart then swallowed the rest of the
  // interaction. Stop chart-panning events at the timebar itself.
  const timebar = document.querySelector('.timebar');
  for (const ev of ['pointerdown', 'pointermove', 'pointerup', 'wheel']) {
    timebar.addEventListener(ev, e => e.stopPropagation());
  }
  // Dragging the slider pauses playback - but only a real drag, not the click
  // that started it.
  slider.addEventListener('pointerdown', () => { if (S.playing) stopPlay(); });

  // sign-in
  $('signin-form').addEventListener('submit', async e => {
    e.preventDefault();
    const v = $('signin-name').value.trim();
    if (!v) return;
    S.watch = v;
    $('signin').hidden = true;
    await post('/api/v2/reset');
    S.alts = (await api(`/api/v2/alternatives?depart_day=${S.depart}`)).items;
    S.offline = await api(`/api/v2/offline?t=${S.t}`);
    await refresh();
    showStage('command_center');
  });

  await refresh();
}

boot().catch(e => { console.error(e); toast('boot failed: ' + e.message); });
