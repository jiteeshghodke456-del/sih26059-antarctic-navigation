/* Provenance — the one place a feature's data status is declared.

   Every panel and every layer names its status here and nowhere else, so a
   panel's marker cannot drift away from what the panel actually does. A test
   asserts that every registered panel and layer appears in this map.

   The marking is deliberately minimal: a small dot before the name, and a
   tooltip. Real bridge software does not explain itself on screen, and the
   master prompt's rule is only that simulated capability must never be
   presented as real - not that it must be shouted about.

     real        no dot      measured or computed from real data
     synthetic   one dot     real physics, synthetic initial conditions -
                             SIMULATED INPUT under section 27, never a forecast
     simulated   two dots    designed, demonstrated, not yet built

   The middle kind was briefly labelled "replay", which was wrong and worth
   recording: replay implies real observations advanced to demo time, and there
   is no real observation anywhere in the world model. The equations are real;
   the state they run on is invented. Calling that replay would be the exact
   class of overclaim the rest of this system exists to prevent.            */

export const PROVENANCE = {
  // --- real: measured data or real computation -----------------------------
  'chart.coast':      ['real', 'Natural Earth 1:50m, public domain'],
  'chart.areas':      ['real', 'ATS protected-area register (ASPA/ASMA)'],
  'chart.graticule':  ['real', 'computed lat/lon grid — no source to cite'],
  'panel.health':     ['real', 'derived from the nine decision gates'],
  'panel.gates':      ['real', 'evaluated from the evidence actually held'],
  'panel.alts':       ['real', 'PolarRoute 1.1.11 + meshiphi 2.3.1, solved offline'],
  'panel.log':        ['real', 'decision log, versioned and attributed'],
  'panel.fresh':      ['real', 'per-layer age computed against the clock'],
  'route.planned':    ['real', 'PolarRoute corridor'],

  // --- synthetic: real physics, invented initial state ---------------------
  'chart.ice':        ['synthetic', 'sea-ice concentration field, modelled forward'],
  'chart.bergs':      ['synthetic', 'iceberg drift, Wagner-Dell-Eisenman 2017 closed form'],
  'chart.wind':       ['synthetic', 'geostrophic wind from the pressure field'],
  'chart.wave':       ['synthetic', 'fetch-limited wave growth from the wind field'],
  'chart.current':    ['synthetic', 'ACC frontal jets'],
  'chart.ownship':    ['synthetic', 'position computed from the planned track, not a GNSS fix'],
  'panel.ice':        ['synthetic', 'sea-ice concentration field'],
  'panel.wx':         ['synthetic', 'wind, sea state and visibility over the corridor'],
  'panel.bergs':      ['synthetic', 'tracked bergs and their predicted separation'],
  'panel.ship':       ['synthetic', 'computed track position'],
  'panel.timeline':   ['synthetic', 'hazard horizon from the forward field'],
  'chart.rio':        ['synthetic', 'POLARIS band under a declared stage and an assumed class'],
  'panel.rio':        ['synthetic', 'POLARIS band — not the IMO RIO, and not a number'],
  'panel.alerts':     ['synthetic', 'raised by gate transitions and field events'],

  // --- simulated: demonstrated, not built ----------------------------------
  'chart.traffic':    ['simulated', 'AIS: no receiver is connected'],
  'chart.warnings':   ['simulated', 'NAVAREA VII warnings: no live feed'],
  'chart.depth':      ['simulated', 'depth contours: GEBCO is not ingested'],
  'panel.sensors':    ['simulated', 'NMEA 0183 from the planned track; no instruments attached'],
  'panel.comms':      ['simulated', 'Iridium link state and shore contact'],
  'panel.escort':     ['simulated', 'icebreaker availability and escort tasking'],
  'panel.science':    ['simulated', 'mission stoppage and station tasking'],
  'panel.offline':    ['simulated', 'pack sync; sizes below are measured, the link is not'],
};

const GLYPH = { real: '', synthetic: '●', simulated: '●●' };

/** Returns a <span> carrying the dot, or null when the feature is real. */
export function dot(key) {
  const p = PROVENANCE[key];
  if (!p) { console.warn('undeclared provenance:', key); return null; }
  const [kind, why] = p;
  if (kind === 'real') return null;
  const s = document.createElement('span');
  s.className = 'pv';
  s.dataset.pv = kind;
  s.textContent = GLYPH[kind];
  s.title = (kind === 'synthetic'
    ? 'Synthetic environment (real physics, invented initial state) — '
    : 'Simulated — ') + why;
  return s;
}

export function kindOf(key) {
  const p = PROVENANCE[key];
  return p ? p[0] : 'unknown';
}
