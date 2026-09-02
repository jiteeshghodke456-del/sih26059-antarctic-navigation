"""Compute a real Cape Town -> Bharati route through real observed sea ice.

Produces the PPT figure that answers "so what?": a ship's route bending around
ice that a satellite actually measured, on a named date.

Routing engine is PolarRoute (British Antarctic Survey, MIT) — the same
institution that operates Antarctic research vessels. We feed it our ice field
through meshiphi's `scalar_csv` dataloader, which is the documented extension
point, so no fork is needed.

Requires Python <=3.11 (PolarRoute does not build on 3.14):
    uv venv --python 3.11 prenv
    uv pip install --python prenv/bin/python polar-route==1.1.11 matplotlib
    ./prenv/bin/python isih/make_route_figure.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
from pyproj import Transformer

from ice_quality import load_sic

# Cape Town harbour -> Bharati station (Larsemann Hills). The real corridor
# India's Antarctic resupply actually sails, per COMPETITIVE_ANALYSIS.md.
CAPE_TOWN = {"name": "Cape Town", "lat": -33.9, "long": 18.4}
BHARATI = {"name": "Bharati", "lat": -69.4, "long": 76.2}

# Bounds must divide evenly by cell size (meshiphi asserts this), and must
# still contain both ports: Cape Town -33.9, Bharati -69.4.
# lat span 40 / 5 = 8 cells; long span 65 / 5 = 13 cells.
MESH_BOUNDS = {"lat_min": -70.0, "lat_max": -30.0, "long_min": 15.0, "long_max": 80.0}


def nsidc_to_dataframe(nc_path: Path, step: int = 2,
                       apply_qa: bool = True) -> pd.DataFrame:
    """Convert one NSIDC file to the lat/long/value table meshiphi expects.

    `step` subsamples the 332x316 grid; the mesh cells are far coarser than
    25 km, so full resolution only costs time.

    `apply_qa` drops cells the CDR's own QA flag marks as land-spillover
    filtered or missing. Those cells are written as 0.0 inside `valid_range`,
    so without this the router reads suppressed coastal pixels as open water
    and plans through them -- see isih/ice_quality.py for the measured case at
    Bharati. Dropping them lets meshiphi fill from the parent cell instead,
    which is the difference between "unknown" and a confident wrong answer.
    """
    sic, _suspect = load_sic(nc_path, apply_qa=apply_qa)
    ds = xr.open_dataset(nc_path)

    transformer = Transformer.from_crs("EPSG:3412", "EPSG:4326", always_xy=True)
    x_grid, y_grid = np.meshgrid(ds.x.values, ds.y.values)
    lon, lat = transformer.transform(x_grid, y_grid)

    lat, lon, sic = lat[::step, ::step], lon[::step, ::step], sic[::step, ::step]
    df = pd.DataFrame({
        "lat": lat.ravel(),
        "long": lon.ravel(),
        "SIC": sic.ravel() * 100.0,   # meshiphi's ice loaders work in percent
    }).dropna()

    inside = (
        df.lat.between(MESH_BOUNDS["lat_min"], MESH_BOUNDS["lat_max"])
        & df["long"].between(MESH_BOUNDS["long_min"], MESH_BOUNDS["long_max"])
    )
    return df[inside].reset_index(drop=True)


def build_mesh(csv_path: Path, date: str, split_depth: int = 4):
    from meshiphi.mesh_generation.mesh_builder import MeshBuilder

    config = {
        "region": {
            "lat_min": MESH_BOUNDS["lat_min"],
            "lat_max": MESH_BOUNDS["lat_max"],
            "long_min": MESH_BOUNDS["long_min"],
            "long_max": MESH_BOUNDS["long_max"],
            "start_time": date,
            "end_time": date,
            "cell_width": 5.0,
            "cell_height": 5.0,
        },
        "data_sources": [
            {"loader": "scalar_csv",
             "params": {"file": str(csv_path), "data_name": "SIC",
                        "value_fill_types": "parent", "splitting_conditions": [
                            {"SIC": {"threshold": 35.0, "upper_bound": 0.9,
                                     "lower_bound": 0.1}}]}},
            # Without thickness and density the ice-resistance speed model
            # silently no-ops (verified in SDA.model_speed source), so the
            # literature lookup tables are wired in deliberately.
            {"loader": "thickness", "params": {"data_name": "thickness"}},
            {"loader": "density", "params": {"data_name": "density"}},
        ],
        "splitting": {"split_depth": split_depth, "minimum_datapoints": 5},
    }

    mesh = MeshBuilder(config).build_environmental_mesh()
    return mesh.to_json()


def route(mesh_json: dict, out_dir: Path) -> dict:
    from polar_route.vessel_performance.vessel_performance_modeller import (
        VesselPerformanceModeller,
    )
    from polar_route.route_planner.route_planner import RoutePlanner

    # MV Vasiliy Golovnin's real published dimensions. Fuel is reported
    # relatively only — the underlying polynomial is fitted to a different
    # vessel (ADR-012), so absolute tonnes would be uncalibrated.
    vessel_config = {
        "vessel_type": "SDA",
        "max_speed": 14.0,
        "unit": "km/hr",
        "beam": 18.6,
        "hull_type": "slender",
        "force_limit": 96634.5,
        "max_ice_conc": 80,
        "min_depth": 20,
        "max_wave": 3.0,
    }

    vpm = VesselPerformanceModeller(mesh_json, vessel_config)
    vpm.model_accessibility()
    vpm.model_performance()
    vessel_mesh = vpm.to_json()

    # PolarRoute requires exactly these capitalised column names, and marks
    # the leg direction with "X" in Source / Destination.
    waypoints = pd.DataFrame([
        {"Name": CAPE_TOWN["name"], "Lat": CAPE_TOWN["lat"],
         "Long": CAPE_TOWN["long"], "Source": "X", "Destination": ""},
        {"Name": BHARATI["name"], "Lat": BHARATI["lat"],
         "Long": BHARATI["long"], "Source": "", "Destination": "X"},
    ])
    wp_path = out_dir / "waypoints.csv"
    waypoints.to_csv(wp_path, index=False)

    planner_config = {
        "objective_function": "traveltime",
        "path_variables": ["fuel", "traveltime"],
        "vector_names": ["uC", "vC"],
        "zero_currents": True,
        "time_unit": "days",
    }

    rp = RoutePlanner(vessel_mesh, planner_config)
    rp.compute_routes(str(wp_path))
    return rp.to_json()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--nsidc-file", type=Path,
                    default=Path("isih/data/nsidc_sic/sic_pss25_20200215_F17_v06r00.nc"))
    ap.add_argument("--out-dir", type=Path, default=Path("isih/figures"))
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    date = args.nsidc_file.name.split("_")[2]
    iso_date = f"{date[:4]}-{date[4:6]}-{date[6:]}"
    print(f"Ice field: {args.nsidc_file.name}  ({iso_date})", flush=True)

    df = nsidc_to_dataframe(args.nsidc_file)
    csv_path = args.out_dir / "sic_points.csv"
    df.to_csv(csv_path, index=False)
    print(f"  {len(df):,} ice points in the corridor", flush=True)

    print("Building mesh …", flush=True)
    mesh_json = build_mesh(csv_path, iso_date)
    print(f"  {len(mesh_json['cellboxes']):,} cells", flush=True)

    print("Routing Cape Town -> Bharati …", flush=True)
    routes = route(mesh_json, args.out_dir)

    (args.out_dir / "mesh.json").write_text(json.dumps(mesh_json))
    (args.out_dir / "routes.json").write_text(json.dumps(routes))
    print(f"\nWrote mesh.json and routes.json to {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
