/* Chart engine — Mercator, pan/zoom, layer stack.

   The previous console drew latitude and longitude on a linear stretch with no
   cos(lat) correction. Measured, that put a degree of longitude 2.92x too wide
   at Bharati (69.4S) and drew Bharati at the same horizontal scale as Cape Town,
   where a degree is 0.42x the length. The route was still correct because
   PolarRoute solves in true coordinates, but a mariner reads a chart by its
   shape and would have seen it immediately.

   Mercator is the right projection here for one specific reason beyond
   familiarity: it is conformal, so a constant course is a straight line, and a
   bearing measured off the screen with a protractor is the bearing you steer.
   It is wrong for polar work above ~80 deg, and our domain stops at 78S. */

export const R = 6378137.0;                 // WGS-84 semi-major, metres
const D2R = Math.PI / 180, R2D = 180 / Math.PI;
const MAXLAT = 85.05112878;                 // Mercator clamp

export function mercY(latDeg) {
  const lat = Math.max(-MAXLAT, Math.min(MAXLAT, latDeg)) * D2R;
  return Math.log(Math.tan(Math.PI / 4 + lat / 2));
}
export function invMercY(y) {
  return (2 * Math.atan(Math.exp(y)) - Math.PI / 2) * R2D;
}
export function mercX(lonDeg) { return lonDeg * D2R; }
export function invMercX(x) { return x * R2D; }

/** Great-circle distance in nautical miles. */
export function distNm(lat1, lon1, lat2, lon2) {
  const p1 = lat1 * D2R, p2 = lat2 * D2R;
  const dp = (lat2 - lat1) * D2R, dl = (lon2 - lon1) * D2R;
  const a = Math.sin(dp / 2) ** 2 + Math.cos(p1) * Math.cos(p2) * Math.sin(dl / 2) ** 2;
  return 2 * R * Math.asin(Math.min(1, Math.sqrt(a))) / 1852;
}

/** Initial great-circle bearing, degrees true. */
export function bearing(lat1, lon1, lat2, lon2) {
  const p1 = lat1 * D2R, p2 = lat2 * D2R, dl = (lon2 - lon1) * D2R;
  const y = Math.sin(dl) * Math.cos(p2);
  const x = Math.cos(p1) * Math.sin(p2) - Math.sin(p1) * Math.cos(p2) * Math.cos(dl);
  return (Math.atan2(y, x) * R2D + 360) % 360;
}

/** Position degrees -> "69 24.3'S" the way a bridge writes it.
    Round first, then carry: 54.99972 must print 55 00.0'S, not 54 60.0'S. */
export function fmtLat(v) { return dm(Math.abs(v), v < 0 ? 'S' : 'N', 2); }
export function fmtLon(v) { return dm(Math.abs(v), v < 0 ? 'W' : 'E', 3); }
function dm(a, hemi, pad) {
  let d = Math.floor(a);
  let m = (a - d) * 60;
  if (Math.round(m * 10) >= 600) { m = 0; d += 1; }
  return String(d).padStart(pad, '0') + '°' + m.toFixed(1).padStart(4, '0') + "'" + hemi;
}

export class Chart {
  constructor(canvas, overlay) {
    this.cv = canvas;
    this.ov = overlay;
    this.ctx = canvas.getContext('2d');
    this.octx = overlay.getContext('2d');
    this.centre = { lat: -50, lon: 47 };
    this.zoom = 1;                  // screen px per 1e-3 mercator unit, scaled below
    this.dpr = Math.min(2, window.devicePixelRatio || 1);
    this.w = 0; this.h = 0;
    this.layers = new Map();        // id -> {draw(ctx, chart), on, order}
    this._drag = null;
    this._bind();
  }

  /* ---- sizing ---- */
  resize() {
    const r = this.cv.parentElement.getBoundingClientRect();
    this.w = r.width; this.h = r.height;
    for (const c of [this.cv, this.ov]) {
      c.width = Math.round(r.width * this.dpr);
      c.height = Math.round(r.height * this.dpr);
    }
    this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    this.octx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
  }

  /** Fit a lat/lon box, leaving a margin fraction. */
  fit(latMin, latMax, lonMin, lonMax, margin = 0.04) {
    const x0 = mercX(lonMin), x1 = mercX(lonMax);
    const y0 = mercY(latMin), y1 = mercY(latMax);
    const sx = (this.w * (1 - 2 * margin)) / Math.abs(x1 - x0);
    const sy = (this.h * (1 - 2 * margin)) / Math.abs(y1 - y0);
    this.scale = Math.min(sx, sy);
    this.centre = { lat: invMercY((y0 + y1) / 2), lon: invMercX((x0 + x1) / 2) };
  }

  /* ---- transforms ---- */
  px(lat, lon) {
    const cx = mercX(this.centre.lon), cy = mercY(this.centre.lat);
    return [
      this.w / 2 + (mercX(lon) - cx) * this.scale,
      this.h / 2 - (mercY(lat) - cy) * this.scale,
    ];
  }
  ll(px, py) {
    const cx = mercX(this.centre.lon), cy = mercY(this.centre.lat);
    return [
      invMercY(cy - (py - this.h / 2) / this.scale),
      invMercX(cx + (px - this.w / 2) / this.scale),
    ];
  }

  /** Metres per screen pixel at a given latitude — for the scale bar. */
  mPerPx(lat) { return R * Math.cos(lat * D2R) / this.scale; }

  /* ---- layers ---- */
  addLayer(id, order, draw, on = true) { this.layers.set(id, { draw, on, order }); }
  toggle(id, on) {
    const l = this.layers.get(id);
    if (l) { l.on = on === undefined ? !l.on : on; this.render(); }
  }
  isOn(id) { const l = this.layers.get(id); return !!(l && l.on); }

  render() {
    const c = this.ctx;
    c.clearRect(0, 0, this.w, this.h);
    const ordered = [...this.layers.values()].filter(l => l.on).sort((a, b) => a.order - b.order);
    for (const l of ordered) {
      c.save();
      try { l.draw(c, this); } catch (e) { console.error('layer draw failed', e); }
      c.restore();
    }
    this._scalebar();
  }

  _scalebar() {
    const el = document.getElementById('scale-bar');
    const lab = document.getElementById('scale-label');
    if (!el || !lab) return;
    const mpp = this.mPerPx(this.centre.lat);
    // choose a round distance close to 110 px
    const targetM = mpp * 110;
    const nice = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000];
    const targetNm = targetM / 1852;
    let pick = nice[nice.length - 1];
    for (const n of nice) { if (n >= targetNm) { pick = n; break; } }
    const wpx = (pick * 1852) / mpp;
    el.style.width = Math.round(wpx) + 'px';
    lab.textContent = pick + ' nm';
  }

  /* ---- interaction ---- */
  _bind() {
    const wrap = this.cv.parentElement;
    wrap.addEventListener('pointerdown', e => {
      this._drag = { x: e.clientX, y: e.clientY, c: { ...this.centre } };
      wrap.setPointerCapture(e.pointerId);
    });
    wrap.addEventListener('pointermove', e => {
      const hud = document.getElementById('hud-cursor');
      const r = wrap.getBoundingClientRect();
      const [la, lo] = this.ll(e.clientX - r.left, e.clientY - r.top);
      if (hud) hud.textContent = fmtLat(la) + '  ' + fmtLon(lo);
      if (this._drag) {
        const dx = (e.clientX - this._drag.x) / this.scale;
        const dy = (e.clientY - this._drag.y) / this.scale;
        this.centre = {
          lon: invMercX(mercX(this._drag.c.lon) - dx),
          lat: invMercY(mercY(this._drag.c.lat) + dy),
        };
        this.render();
        if (this.onmove) this.onmove();
      } else if (this.onhover) {
        this.onhover(la, lo, e.clientX - r.left, e.clientY - r.top);
      }
    });
    const end = e => { this._drag = null; try { wrap.releasePointerCapture(e.pointerId); } catch {} };
    wrap.addEventListener('pointerup', end);
    wrap.addEventListener('pointercancel', end);
    wrap.addEventListener('pointerleave', () => {
      this._drag = null;
      if (this.onhover) this.onhover(null);
    });
    wrap.addEventListener('wheel', e => {
      e.preventDefault();
      const r = wrap.getBoundingClientRect();
      const mx = e.clientX - r.left, my = e.clientY - r.top;
      const before = this.ll(mx, my);
      const k = Math.exp(-e.deltaY * 0.0013);
      this.scale = Math.max(20, Math.min(90000, this.scale * k));
      const after = this.ll(mx, my);
      // keep the point under the cursor fixed
      this.centre = {
        lat: invMercY(mercY(this.centre.lat) + (mercY(before[0]) - mercY(after[0]))),
        lon: invMercX(mercX(this.centre.lon) + (mercX(before[1]) - mercX(after[1]))),
      };
      this.render();
      if (this.onmove) this.onmove();
    }, { passive: false });
  }
}

/* ---- shared drawing helpers ---------------------------------------------- */

export function polyPath(ctx, chart, ring) {
  ctx.beginPath();
  for (let i = 0; i < ring.length; i++) {
    const [lon, lat] = ring[i];
    const [x, y] = chart.px(lat, lon);
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }
}

/** Graticule with degrees-and-minutes labels, spacing chosen from the zoom. */
export function drawGraticule(ctx, chart, colour, labelColour) {
  const [latT, lonL] = chart.ll(0, 0);
  const [latB, lonR] = chart.ll(chart.w, chart.h);
  const span = Math.max(Math.abs(latT - latB), Math.abs(lonR - lonL));
  const steps = [30, 20, 10, 5, 2, 1, 0.5, 0.25];
  let step = steps[0];
  for (const s of steps) { if (span / s <= 9) { step = s; break; } }

  ctx.strokeStyle = colour;
  ctx.fillStyle = labelColour;
  ctx.lineWidth = 0.5;
  ctx.font = '9px ui-monospace, monospace';
  ctx.setLineDash([1, 3]);

  const lat0 = Math.ceil(Math.min(latT, latB) / step) * step;
  for (let la = lat0; la <= Math.max(latT, latB); la += step) {
    const [, y] = chart.px(la, chart.centre.lon);
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(chart.w, y); ctx.stroke();
    ctx.fillText(fmtLat(la), 3, y - 2);
  }
  const lon0 = Math.ceil(Math.min(lonL, lonR) / step) * step;
  for (let lo = lon0; lo <= Math.max(lonL, lonR); lo += step) {
    const [x] = chart.px(chart.centre.lat, lo);
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, chart.h); ctx.stroke();
    ctx.save();
    ctx.translate(x + 2, chart.h - 4);
    ctx.fillText(fmtLon(lo), 0, 0);
    ctx.restore();
  }
  ctx.setLineDash([]);

  // the Antarctic Circle is a real navigational reference, drawn solid
  if (Math.min(latT, latB) < -66.5606 && Math.max(latT, latB) > -66.5606) {
    const [, y] = chart.px(-66.5606, chart.centre.lon);
    ctx.strokeStyle = labelColour;
    ctx.setLineDash([6, 4]);
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(chart.w, y); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillText('ANTARCTIC CIRCLE', chart.w - 108, y - 3);
  }
}
