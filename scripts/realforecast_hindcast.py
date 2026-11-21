#!/usr/bin/env python3
"""The honest test (HANDOFF_TONIGHT slice 2): score the trained U-Net with the
real Copernicus *forecast* as background against real satellite truth.

    python scripts/realforecast_hindcast.py [--no-model]

For each clean archived cycle t and lead L in {1,3,5,7}:
    raw CMEMS    = cycle t, step L (regridded to the NSIDC 25 km grid)
    persistence  = NSIDC NRT observation at t, carried forward
    U-Net        = clip(raw + model correction, 0, 1), inputs built by
                   isih.features.build_channels_operational — only data
                   knowable on day t
    truth        = NSIDC NRT G10016 v4 at t+L, QA-masked (isih.ice_quality)

Scored only on valid cells inside the Copernicus box (0–80E, 55–78S), RMSE
pooled over cycles (training convention: zero-filled fields over the
isfinite(forecast) & isfinite(truth) mask) and mean IIEE at the 15% threshold.

Scored once, reported as it comes out — no re-tuning on this set, ever.

Also importable (scripts/resolution_study.py, F1): `run(factors=(1, 3, 12))`
scores the same cycles with the forecast block-averaged to ~1/4° and ~1°.
Coarsened fields are repeated back onto the native 1/12° grid and every factor
is scored on the SAME valid-cell mask, so the only thing that varies is the
information content of the forecast — not the scoring geometry.

Caveats carried into the output JSON:
- sensor change: NRT v4 uses AMSR2 since 2025-01-01; training truth was F17
  SSMIS (G02202 v6). A known distribution shift.
- region: corridor only, not the hemisphere the model was trained on.
- sample: ~76 forecast cycles from one spring season (2026-08-31 onward).
- latency: assumes the day-t satellite file is in hand on day t, the same
  assumption the training setup makes.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import xarray as xr

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "isih"))
sys.path.insert(0, str(ROOT))

from features import N_HISTORY, build_channels_operational, iiee_km2  # noqa: E402
from grid import GlorysToNsidcRegridder, nsidc_lonlat  # noqa: E402
from ice_quality import load_sic  # noqa: E402

ARCHIVE = ROOT / "data" / "cmems_forecast_archive"
NRT_DIR = ROOT / "data" / "nsidc_nrt"
OUT = ROOT / "isih" / "figures" / "realforecast_hindcast.json"
LEADS = (1, 3, 5, 7)
BOX = {"lon": (0.0, 80.0), "lat": (-78.0, -55.0)}

CAVEATS = [
    "sensor change: truth is AMSR2 since 2025-01-01, training truth was F17 SSMIS",
    "corridor only, not the training hemisphere",
    "one spring season, ~76 cycles",
    "assumes day-t satellite file available on day t (training's assumption too)",
    "4 stale cycles excluded per KNOWN_STALE.md",
]


def clean_cycles() -> dict[dt.date, xr.Dataset]:
    """Cycles with exactly 10 daily steps starting on the cycle date —
    the same rule scripts/score_cmems_archive.py and KNOWN_STALE.md use."""
    out = {}
    for path in sorted(ARCHIVE.glob("cmems_siconc_*.nc")):
        day = dt.date.fromisoformat(path.name[13:23])
        ds = xr.open_dataset(path)
        steps = ds.time.values.astype("datetime64[D]")
        if len(steps) == 10 and (steps == np.datetime64(day) + np.arange(10)).all():
            out[day] = ds
        else:
            ds.close()
    return out


def load_nrt() -> dict[dt.date, np.ndarray]:
    obs = {}
    for path in sorted(NRT_DIR.glob("sic_pss25_*.nc")):
        day = dt.datetime.strptime(path.name.split("_")[2], "%Y%m%d").date()
        sic, _ = load_sic(path)
        obs[day] = sic
    return obs


def block_coarsen(field2d: np.ndarray, f: int) -> np.ndarray:
    """nanmean over f×f blocks, repeated back to the original shape.
    Trailing rows/cols that don't fill a block become NaN (and are then
    excluded from every factor's scoring by the common mask)."""
    if f == 1:
        return field2d
    ny, nx = field2d.shape
    ny2, nx2 = ny // f * f, nx // f * f
    a = field2d[:ny2, :nx2].reshape(ny2 // f, f, nx2 // f, f)
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Mean of empty slice")
        m = np.nanmean(a, axis=(1, 3))
    out = np.full_like(field2d, np.nan)
    out[:ny2, :nx2] = np.repeat(np.repeat(m, f, 0), f, 1)
    return out


def run(factors: tuple[int, ...] = (1,), use_model: bool = True) -> dict:
    """Score every factor over the same cycles and the same mask.
    Returns {factor: {lead: {n_cycles, rmse{...}, iiee_km2_mean{...}}}}."""
    cycles = clean_cycles()
    obs = load_nrt()
    print(f"clean cycles: {len(cycles)}, NRT days: {len(obs)}, factors: {factors}")

    template = xr.open_dataset(next(iter(NRT_DIR.glob("sic_pss25_*.nc"))))
    first = next(iter(cycles.values()))
    rg = GlorysToNsidcRegridder(template, first["latitude"].values,
                                first["longitude"].values)
    print(f"regridder coverage of NSIDC grid: {rg.coverage()*100:.1f}%")

    lon, lat = nsidc_lonlat(template)
    box = ((lon >= BOX["lon"][0]) & (lon <= BOX["lon"][1])
           & (lat >= BOX["lat"][0]) & (lat <= BOX["lat"][1]))

    models = {}
    if use_model:
        import torch
        from model_io import load_checkpoint
        for lead in LEADS:
            models[lead] = load_checkpoint(lead)

    results: dict[int, dict] = {f: {} for f in factors}
    for lead in LEADS:
        acc = {f: {"se": {"cmems": 0.0, "persistence": 0.0, "unet": 0.0},
                   "cnt": 0.0,
                   "iiee": {"cmems": [], "persistence": [], "unet": []}}
               for f in factors}
        n = 0
        used_dates = []
        for day, ds in sorted(cycles.items()):
            target_day = day + dt.timedelta(days=lead)
            history_days = [day - dt.timedelta(days=k) for k in range(N_HISTORY)]
            if target_day not in obs or any(d not in obs for d in history_days):
                continue

            fc_src = ds["siconc"].isel(time=lead).values.astype(np.float32)
            an_src = ds["siconc"].isel(time=0).values.astype(np.float32)
            history = np.stack([obs[d] for d in history_days])
            truth = obs[target_day]
            truth_f = np.nan_to_num(truth, nan=0.0)

            fc = {f: rg(block_coarsen(fc_src, f)) for f in factors}
            an = {f: rg(block_coarsen(an_src, f)) for f in factors}

            # one mask for every factor: finite everywhere, in the box
            mask = np.isfinite(truth) & box
            for f in factors:
                mask &= np.isfinite(fc[f])
            if mask.sum() == 0:
                continue

            for f in factors:
                x, _ = build_channels_operational(
                    fc[f], an[f], history, int(target_day.strftime("%Y%m%d")))
                preds = {"cmems": x[0, 0], "persistence": x[0, 1]}
                if models:
                    import torch
                    with torch.no_grad():
                        delta = models[lead](torch.from_numpy(x))[0, 0].numpy()
                    preds["unet"] = np.clip(x[0, 0] + delta, 0.0, 1.0)
                a = acc[f]
                for name, p in preds.items():
                    a["se"][name] += float((((p - truth_f) ** 2) * mask).sum())
                    a["iiee"][name].append(iiee_km2(p, truth_f, mask))
                a["cnt"] += float(mask.sum())
            n += 1
            used_dates.append(str(day))

        for f in factors:
            a = acc[f]
            results[f][f"lead_{lead}"] = {
                "n_cycles": n,
                "first_cycle": used_dates[0] if used_dates else None,
                "last_cycle": used_dates[-1] if used_dates else None,
                "rmse": {k: round((v / a["cnt"]) ** 0.5, 5)
                         for k, v in a["se"].items() if a["iiee"][k]},
                "iiee_km2_mean": {k: round(float(np.mean(v)), 0)
                                  for k, v in a["iiee"].items() if v},
            }
        line = " | ".join(
            f"1/{12//f}°" if f in (1, 3) else "1°" for f in factors)
        print(f"lead {lead}: n={n} ({line}) " + " ".join(
            f"f{f}:cmems={results[f][f'lead_{lead}']['rmse']['cmems']}"
            for f in factors))
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-model", action="store_true",
                    help="baselines only (checkpoints not yet on disk)")
    args = ap.parse_args()

    results = run(factors=(1,), use_model=not args.no_model)
    payload = {
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "truth": "NOAA/NSIDC G10016 v4 NRT (AMSR2), QA-masked",
        "forecast": "CMEMS GLO12 cmems_mod_glo_phy_anfc, archived at issue time",
        "model": None if args.no_model else
                 "re-run 2026-11-21 of the 2026-08-31 Kaggle training "
                 "(identical code, seed and split; credentials cell only change)",
        "scoring": "corridor box 0-80E 55-78S, pooled RMSE on zero-filled "
                   "fields over isfinite(forecast)&isfinite(truth) cells "
                   "(training convention), IIEE at 15% threshold",
        "caveats": CAVEATS,
        "leads": results[1],
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
