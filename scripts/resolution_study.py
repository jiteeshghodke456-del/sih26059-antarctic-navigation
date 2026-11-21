#!/usr/bin/env python3
"""F1: does ocean-model resolution change the navigation answer?

    python scripts/resolution_study.py [--no-model]

Takes the same archived GLO12 forecasts and block-averages them from 1/12°
to ~1/4° (factor 3) and ~1° (factor 12), then scores each against the same
NSIDC NRT truth on the same cells (scripts/realforecast_hindcast.run), at
leads 1, 3, 5, 7. Persistence and the satellite history are untouched — only
the ocean model's information content varies.

Stated caveat, printed into the JSON and the write-up: coarsening one model's
output is NOT the same as running a coarser model — it removes resolved
structure but keeps 1/12°-informed physics (eddies already shaped the mean).
A true resolution experiment needs the same model run at several resolutions,
e.g. the ANHA configurations; the NEMO reader (F2) is what would let those
runs drop into this exact pipeline.

Writes dakshin/figures/resolution_study.json and resolution_study.png.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from realforecast_hindcast import CAVEATS, LEADS, run  # noqa: E402

OUT_JSON = ROOT / "dakshin" / "figures" / "resolution_study.json"
OUT_PNG = ROOT / "dakshin" / "figures" / "resolution_study.png"
FACTORS = {1: "1/12°", 3: "1/4°", 12: "1°"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-model", action="store_true")
    args = ap.parse_args()

    results = run(factors=tuple(FACTORS), use_model=not args.no_model)

    payload = {
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "question": "does a 1/12° ocean model tell the captain something a "
                    "coarser model would miss?",
        "method": "same forecasts block-averaged to each resolution, repeated "
                  "back to the native grid, scored on identical cells; "
                  "truth and persistence unchanged",
        "caveat": "coarsening one model is not running a coarser model — "
                  "a true test needs e.g. ANHA runs at several resolutions "
                  "(see F2, the NEMO-native reader)",
        "hindcast_caveats": CAVEATS,
        "resolutions": {FACTORS[f]: res for f, res in results.items()},
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {OUT_JSON}")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for f, label in FACTORS.items():
        leads = list(LEADS)
        rmse = [results[f][f"lead_{k}"]["rmse"]["cmems"] for k in leads]
        iiee = [results[f][f"lead_{k}"]["iiee_km2_mean"]["cmems"] / 1e3
                for k in leads]
        axes[0].plot(leads, rmse, marker="o", label=f"CMEMS @ {label}")
        axes[1].plot(leads, iiee, marker="o", label=f"CMEMS @ {label}")
    pers = [results[1][f"lead_{k}"]["rmse"]["persistence"] for k in LEADS]
    axes[0].plot(LEADS, pers, marker="s", ls="--", color="gray",
                 label="persistence (satellite)")
    pers_i = [results[1][f"lead_{k}"]["iiee_km2_mean"]["persistence"] / 1e3
              for k in LEADS]
    axes[1].plot(LEADS, pers_i, marker="s", ls="--", color="gray",
                 label="persistence (satellite)")
    if not args.no_model:
        unet = [results[1][f"lead_{k}"]["rmse"].get("unet") for k in LEADS]
        if all(unet):
            axes[0].plot(LEADS, unet, marker="^", color="tab:red",
                         label="U-Net @ 1/12°")
            unet_i = [results[1][f"lead_{k}"]["iiee_km2_mean"]["unet"] / 1e3
                      for k in LEADS]
            axes[1].plot(LEADS, unet_i, marker="^", color="tab:red",
                         label="U-Net @ 1/12°")
    axes[0].set_xlabel("lead (days)"); axes[0].set_ylabel("RMSE (SIC fraction)")
    axes[1].set_xlabel("lead (days)"); axes[1].set_ylabel("IIEE (10³ km²)")
    axes[0].set_title("Ice-edge skill vs model resolution")
    axes[1].set_title("Extent-edge error vs model resolution")
    for ax in axes:
        ax.grid(alpha=0.3); ax.legend(fontsize=8)
    fig.suptitle("Corridor 0–80E 55–78S, 2026 spring, truth = NSIDC NRT (AMSR2)",
                 fontsize=9, y=1.02)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=150, bbox_inches="tight")
    print(f"wrote {OUT_PNG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
