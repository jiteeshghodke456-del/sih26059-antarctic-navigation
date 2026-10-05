"""When does the destination stop being reachable?

The route experiment turned up something sharper than a transit-time delta.
On 1 December 2019 the ice at Bharati looks passable, so a planner commits to
it. Nine days later the same cell is 96% ice and closed to this vessel.

A ship planning on departure-day ice cannot see that. It is not a routing
error -- the route was optimal for the information available -- it is an
*information* error, and it is exactly the gap a lead-time forecast fills.

This script measures the closure directly: for each day, is the destination
cell passable for MV Vasiliy Golovnin, and at what concentration?

    prenv/bin/python isih/destination_window.py --start 2019-12-01 --days 30
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

from ice_meshes import GOLOVNIN, CellLookup, vessel_mesh_for

# Bharati sits on the Larsemann Hills coast, so its own cell is a real
# ship-accessible target. Maitri is deliberately NOT here: it lies inland in
# the Schirmacher Oasis and is resupplied across the ice shelf from an offload
# point we have not yet sourced, so scoring "is Maitri's cell passable" would
# be measuring nothing. Add it once the real offload position is confirmed.
TARGETS = {
    "Bharati": (-69.4, 76.2),
    "Bharati approach (100 km N)": (-68.5, 76.2),
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start", default="2019-12-01")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--out", type=Path,
                    default=Path("isih/figures/destination_window.json"))
    args = ap.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d").date()

    rows = []
    for offset in range(args.days):
        day = start + timedelta(days=offset)
        try:
            qa_on = CellLookup(vessel_mesh_for(day, apply_qa=True))
            qa_off = CellLookup(vessel_mesh_for(day, apply_qa=False))
        except FileNotFoundError:
            break

        row = {"date": f"{day:%Y-%m-%d}", "day": offset}
        for name, (lat, lon) in TARGETS.items():
            sic_on = qa_on.sic_at(lat, lon)
            sic_off = qa_off.sic_at(lat, lon)
            spd_on = qa_on.speed_at(lat, lon)
            row[name] = {
                "sic_qa_on": None if sic_on is None else round(sic_on, 1),
                "sic_qa_off": None if sic_off is None else round(sic_off, 1),
                "passable": spd_on is not None and spd_on > 0,
            }
        rows.append(row)
        print(f"  {row['date']}  " + "  ".join(
            f"{n.split()[0]}: {row[n]['sic_qa_on']}% "
            f"{'OPEN' if row[n]['passable'] else 'CLOSED'}"
            for n in TARGETS), flush=True)

    # First day each target closes, and whether it reopens.
    summary = {}
    for name in TARGETS:
        closed_days = [r["day"] for r in rows if not r[name]["passable"]]
        summary[name] = {
            "days_observed": len(rows),
            "days_closed": len(closed_days),
            "first_closed_day": closed_days[0] if closed_days else None,
            "first_closed_date": (rows[closed_days[0]]["date"]
                                  if closed_days else None),
            "pct_days_closed": (round(100.0 * len(closed_days) / len(rows), 1)
                                if rows else None),
        }

    out = {
        "vessel": "MV Vasiliy Golovnin",
        "ice_limit_pct": GOLOVNIN["max_ice_conc"],
        "start": args.start,
        "note": ("sic_qa_off is what an unguarded reader sees; where it is 0.0 "
                 "and sic_qa_on is not, the CDR land-spillover filter had "
                 "suppressed that cell and written it as open water."),
        "summary": summary,
        "daily": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2))
    print("\n" + json.dumps(summary, indent=2))
    print(f"\nWrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
