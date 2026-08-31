"""Build the ISIH prototype training set: paired (GLORYS12 background, NSIDC truth).

Runs anywhere with CMEMS credentials — a Kaggle CPU notebook is the intended
home (see isih/kaggle/), because that is where training happens and it keeps
credentials in Kaggle Secrets rather than on anyone's laptop.

Output: one compressed .npz per year holding aligned arrays on the NSIDC grid,
plus a manifest recording exactly what was built and from where.

    background : (n_days, ny, nx) float32  GLORYS12 siconc, regridded
    truth      : (n_days, ny, nx) float32  NSIDC observed SIC
    valid_mask : (n_days, ny, nx) bool     both fields present and QC-clean
    dates      : (n_days,)        int32    YYYYMMDD

The model learns `truth - background`; the mask marks where that target is
real. Nothing is imputed here — a missing cell stays masked rather than being
filled with a guess that would train the model on fiction.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import xarray as xr

from isih.grid import GlorysToNsidcRegridder

GLORYS_DATASET = "cmems_mod_glo_phy_my_0.083deg_P1D-m"
# Corridor sector, matching ADR-001's scoping decision. A margin is kept
# around it so regridding near the edge still has source cells to average.
CORRIDOR = dict(min_lon=-5.0, max_lon=85.0, min_lat=-80.0, max_lat=-48.0)


def load_nsidc_year(nsidc_dir: Path, year: int) -> tuple[np.ndarray, np.ndarray, xr.Dataset]:
    """Return (truth stack, dates, a template dataset for grid geometry)."""
    files = sorted(nsidc_dir.glob(f"sic_pss25_{year}*.nc"))
    if not files:
        raise FileNotFoundError(f"no NSIDC files for {year} in {nsidc_dir}")

    template = xr.open_dataset(files[0])
    truth, dates = [], []
    for path in files:
        with xr.open_dataset(path) as ds:
            sic = ds["cdr_seaice_conc"].isel(time=0).values.astype(np.float32)
            # Flag values live above 1.0 in this product (pole hole, land,
            # missing). Valid concentration is a fraction in [0, 1].
            sic = np.where((sic >= 0.0) & (sic <= 1.0), sic, np.nan)
            truth.append(sic)
            stamp = path.name.split("_")[2]
            dates.append(int(stamp))
    return np.stack(truth), np.asarray(dates, dtype=np.int32), template


def fetch_glorys_year(year: int, out_dir: Path) -> Path:
    """Download one year of GLORYS12 siconc over the corridor."""
    import copernicusmarine

    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"glorys_siconc_{year}.nc"
    if target.exists() and target.stat().st_size > 10_000:
        print(f"  [{year}] GLORYS12 already present, skipping download")
        return target

    print(f"  [{year}] downloading GLORYS12 siconc …", flush=True)
    copernicusmarine.subset(
        dataset_id=GLORYS_DATASET,
        variables=["siconc"],
        start_datetime=f"{year}-01-01T00:00:00",
        end_datetime=f"{year}-12-31T00:00:00",
        minimum_longitude=CORRIDOR["min_lon"],
        maximum_longitude=CORRIDOR["max_lon"],
        minimum_latitude=CORRIDOR["min_lat"],
        maximum_latitude=CORRIDOR["max_lat"],
        output_directory=str(out_dir),
        output_filename=target.name,
        overwrite=True,
    )
    return target


def build_year(year: int, nsidc_dir: Path, glorys_dir: Path, out_dir: Path) -> dict:
    print(f"[{year}] building …", flush=True)
    truth, dates, template = load_nsidc_year(nsidc_dir, year)

    glorys_path = fetch_glorys_year(year, glorys_dir)
    gl = xr.open_dataset(glorys_path)

    regridder = GlorysToNsidcRegridder(
        template, gl["latitude"].values, gl["longitude"].values
    )
    coverage = regridder.coverage()
    print(f"  [{year}] corridor covers {coverage * 100:.1f}% of the NSIDC grid", flush=True)

    # Align on dates present in both sources; a day missing from either is
    # dropped, not interpolated.
    gl_dates = np.array(
        [int(str(d)[:10].replace("-", "")) for d in gl["time"].dt.strftime("%Y-%m-%d").values],
        dtype=np.int32,
    )
    common, nsidc_idx, glorys_idx = np.intersect1d(dates, gl_dates, return_indices=True)
    print(f"  [{year}] {len(common)} days present in both sources", flush=True)

    truth = truth[nsidc_idx]
    background = np.stack(
        [regridder(gl["siconc"].isel(time=int(i)).values.astype(np.float32))
         for i in glorys_idx]
    )

    valid = np.isfinite(truth) & np.isfinite(background)
    print(f"  [{year}] valid cells: {valid.mean() * 100:.1f}%", flush=True)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"isih_pairs_{year}.npz"
    np.savez_compressed(
        out_path,
        background=np.nan_to_num(background, nan=0.0).astype(np.float32),
        truth=np.nan_to_num(truth, nan=0.0).astype(np.float32),
        valid_mask=valid,
        dates=common.astype(np.int32),
    )
    size_mb = out_path.stat().st_size / 1e6
    print(f"  [{year}] wrote {out_path.name} ({size_mb:.0f} MB)", flush=True)

    return {
        "year": year,
        "days": int(len(common)),
        "valid_fraction": float(valid.mean()),
        "grid_coverage": float(coverage),
        "file": out_path.name,
        "size_mb": round(size_mb, 1),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--years", type=int, nargs="+", default=[2018, 2019, 2020])
    ap.add_argument("--nsidc-dir", type=Path, default=Path("isih/data/nsidc_sic"))
    ap.add_argument("--glorys-dir", type=Path, default=Path("isih/data/glorys"))
    ap.add_argument("--out-dir", type=Path, default=Path("isih/data/pairs"))
    args = ap.parse_args()

    summaries = [
        build_year(y, args.nsidc_dir, args.glorys_dir, args.out_dir)
        for y in args.years
    ]

    manifest = {
        "built_at": datetime.utcnow().isoformat() + "Z",
        "purpose": "ISIH prototype (Sept 8) — NOT the December production dataset",
        "background_source": GLORYS_DATASET,
        "truth_source": "NOAA/NSIDC CDR G02202_V6 south daily",
        "region": CORRIDOR,
        "grid": "NSIDC 25km south polar stereographic, EPSG:3412",
        "regridding": "area-average of GLORYS12 cells into NSIDC cells; truth never resampled",
        "years": summaries,
    }
    manifest_path = args.out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"\nManifest: {manifest_path}")
    print(f"Total days: {sum(s['days'] for s in summaries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
