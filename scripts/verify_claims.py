"""Check every quantitative claim in SIH_PPT.md / TRUE_CLAIMS.md against source."""
import json
from pathlib import Path

R = Path('/home/jiteesh/sih/SIH26059-antarctic-navigation/.claude/worktrees/'
         'foamy-seeking-allen')

ok, bad = [], []


def check(label, actual, expected):
    (ok if actual == expected else bad).append(
        f"{label}: claimed {expected!r}, actual {actual!r}")


q = json.loads((R / 'isih/figures/ice_quality_audit.json').read_text())
check("Bharati QA-affected days %",
      q['station_approaches']['Bharati']['pct_of_days_affected'], 43.2)
check("archive file count", q['archive']['files'], 1096)
check("spillover days affected", q['land_spillover']['days_affected'], 1096)
check("spillover mean cells/day",
      q['land_spillover']['mean_cells_per_day'], 118.2)

d = json.loads((R / 'isih/figures/destination_window.json').read_text())
check("Bharati days closed", d['summary']['Bharati']['days_closed'], 23)
check("Bharati days observed", d['summary']['Bharati']['days_observed'], 31)
check("approach days closed",
      d['summary']['Bharati approach (100 km N)']['days_closed'], 0)
open_days = [r for r in d['daily'] if r['Bharati']['passable']]
check("Bharati open days", len(open_days), 8)
artifacts = [r for r in open_days if r['Bharati']['sic_qa_off'] == 0.0]
check("open days that are artifacts", len(artifacts), 4)

g = json.loads((R / 'models/iceberg/regime_report.json').read_text())
check("icebergs tracked", g['catalogue']['icebergs'], 33)
check("bergs in corridor", g['corridor']['n_bergs'], 15)
check("largest berg", g['catalogue']['largest'], 'D15A')
check("largest area km2", g['catalogue']['largest_area_km2'], 3037.47)
check("current-dominated at typical",
      g['regime']['typical_forcing']['n_current_dominated_R_lt_0p1'], 20)
check("wind-dominated at storm",
      g['regime']['storm_forcing']['n_wind_dominated_R_gt_1'], 28)

rr = json.loads((R / 'isih/figures/route_regret.json').read_text())
static = [r for r in rr['results'] if r['planner'] == 'STATIC'][0]
check("static regret days", static['regret_days'], 0.03)
check("transit days (rounded)", round(static['actual_days'], 1), 8.6)

res = (R / 'isih/RESULTS.md').read_text()
for token in ["+18.5%", "+30.6%", "1,929,601", "43.2%", "46.8%", "54.6%",
              "23 / 31", "8.58"]:
    (ok if token in res else bad).append(f"RESULTS.md contains {token!r}")

for f in ["docs/SIH_PPT.md", "docs/TRUE_CLAIMS.md",
          "models/iceberg/drift.py", "models/iceberg/catalogue.py"]:
    (ok if (R / f).exists() else bad).append(f"file exists: {f}")

print(f"PASSED {len(ok)}")
if bad:
    print(f"\nFAILED {len(bad)}:")
    for b in bad:
        print("  -", b)
else:
    print("All claims verified against source files.")
