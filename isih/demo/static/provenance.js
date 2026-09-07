/* Provenance — the one place a feature's data status is declared.

   Every panel and every layer names its status here and nowhere else, so a
   panel's marker cannot drift away from what the panel actually does. A test
   asserts that every registered panel and layer appears in this map.

   The marking is deliberately minimal: a small dot before the name, and a
   tooltip. Real bridge software does not explain itself on screen, and the
   master prompt's rule is only that simulated capability must never be
   presented as real - not that it must be shouted about.

     real       no dot      measured or computed from real data
     replay     one dot     real data, replayed or modelled forward
     simulated  two dots    designed, demonstrated, not yet built            */

export const PROVENANCE = {
  // --- real: measured data or real computation -----------------------------
  'chart.coast':      ['real', 'Natural Earth 1:50m, public domain'],
  'chart.areas':      ['real', 'ATS protected-area register (ASPA/ASMA)'],
  'panel.health':     ['real', 'derived from the nine decision gates'],
  'panel.gates':      ['real', 'evaluated from the evidence actually held'],
  'panel.alts':       ['real', 'PolarRoute 1.1.11 + meshiphi 2.3.1, solved offline'],
  'panel.log':        ['real', 'decision log, versioned and attributed'],
  'panel.fresh':      ['real', 'per-layer age computed against the clock'],
  'route.planned':    ['real', 'PolarRoute corridor'],

  // --- replay: real physics or real data, advanced to demo time ------------
  'chart.ice':        ['replay', 'sea-ice concentration field, modelled forward'],
  'chart.bergs':      ['replay', 'iceberg drift, Wagner-Dell-Eisenman 2017 closed form'],
  'chart.wind':       ['replay', 'geostrophic wind from the pressure field'],
  'chart.wave':       ['replay', 'fetch-limited wave growth from the wind field'],
  'chart.current':    ['replay', 'ACC frontal jets'],
  'chart.ownship':    ['replay', 'position computed from the planned track, not a GNSS fix'],
  'panel.ice':        ['replay', 'sea-ice concentration field'],
  'panel.wx':         ['replay', 'wind, sea state and visibility over the corridor'],
  'panel.bergs':      ['replay', 'tracked bergs and their predicted separation'],
  'panel.ship':       ['replay', 'computed track position'],
  'panel.timeline':   ['replay', 'hazard horizon from the forward field'],
  'panel.alerts':     ['replay', 'raised by gate transitions and field events'],

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

const GLYPH = { real: '', replay: '●', simulated: '●●' };

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
  s.title = (kind === 'replay' ? 'Replayed / modelled — ' : 'Simulated — ') + why;
  return s;
}

export function kindOf(key) {
  const p = PROVENANCE[key];
  return p ? p[0] : 'unknown';
}
