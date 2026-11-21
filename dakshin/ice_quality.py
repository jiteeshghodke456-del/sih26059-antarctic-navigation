"""Quality control for NSIDC CDR sea-ice concentration.

Why this module exists
----------------------
The NOAA/NSIDC CDR applies a *land spillover filter* to coastal cells, because
a 25 km passive-microwave footprint that overlaps land reads warm and would be
mistaken for open water. When that filter fires, the product writes **0.0** --
not a fill value. Zero is inside `valid_range [0, 100]`, so every naive reader
accepts it as "open water".

That is not a hypothetical. On 2019-12-01 the cell at 69.1 S, 75.9 E -- 35 km
off Bharati station -- reads 0.0 with `cdr_seaice_conc_qa_flag = 4`
(Land_spillover_filter_applied), sitting directly beside cells reading 0.60.
Three days later the same cell reads 0.90. The ice never left; the retrieval did.

Consequences we measured:
  * routing  - the planner treated those cells as open water and routed the ship
               into what was really 90%+ ice, at the station approach, which is
               the most safety-critical part of the voyage.
  * training - the same zeros are in the model's training targets, concentrated
               exactly at the coast where a resupply ship most needs accuracy.

So we read the QA flag the product ships and stop trusting those cells.

Flag bits (from the file's own `flag_masks` / `flag_meanings`):
    1  BT_weather_filter_applied
    2  NT_weather_filter_applied
    4  Land_spillover_filter_applied
    8  No_input_data
   16  invalid_ice_mask_applied
   32  spatial_interpolation_applied
   64  temporal_interpolation_applied
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import xarray as xr

QA_BT_WEATHER = 1
QA_NT_WEATHER = 2
QA_LAND_SPILLOVER = 4
QA_NO_INPUT = 8
QA_INVALID_ICE_MASK = 16
QA_SPATIAL_INTERP = 32
QA_TEMPORAL_INTERP = 64

QA_LABELS = {
    QA_BT_WEATHER: "BT weather filter",
    QA_NT_WEATHER: "NT weather filter",
    QA_LAND_SPILLOVER: "land spillover filter",
    QA_NO_INPUT: "no input data",
    QA_INVALID_ICE_MASK: "invalid ice mask",
    QA_SPATIAL_INTERP: "spatial interpolation",
    QA_TEMPORAL_INTERP: "temporal interpolation",
}

# Bits that make a *concentration value* untrustworthy rather than merely
# derived. Spillover and no-input write a number we must not believe.
# Interpolation bits are kept: an interpolated value is still an estimate, and
# discarding them would throw away most of the coastal record.
UNTRUSTWORTHY = QA_LAND_SPILLOVER | QA_NO_INPUT


def load_sic(path: Path | str, apply_qa: bool = True
             ) -> tuple[np.ndarray, np.ndarray]:
    """Load one CDR day.

    Returns `(sic, suspect)` where `sic` is concentration in 0..1 with invalid
    and (optionally) QA-suspect cells set to NaN, and `suspect` is the boolean
    mask of cells the QA flag told us not to believe.

    Setting suspect cells to NaN rather than to a guess is deliberate: downstream
    the mesh builder drops NaN and meshiphi fills from the parent cell, so an
    unknown coastal cell inherits its surroundings instead of asserting open
    water. "I don't know" routes a ship more safely than a confident zero.
    """
    ds = xr.open_dataset(path)
    sic = ds["cdr_seaice_conc"].isel(time=0).values.astype(np.float32)
    sic = np.where((sic >= 0.0) & (sic <= 1.0), sic, np.nan)

    suspect = np.zeros(sic.shape, dtype=bool)
    if apply_qa and "cdr_seaice_conc_qa_flag" in ds:
        qa = ds["cdr_seaice_conc_qa_flag"].isel(time=0).values
        qa = np.nan_to_num(qa, nan=0).astype(np.int32)
        suspect = (qa & UNTRUSTWORTHY) != 0
        sic = np.where(suspect, np.nan, sic)

    return sic, suspect


def load_stdev(path: Path | str) -> np.ndarray:
    """Per-pixel retrieval standard deviation the CDR ships alongside SIC.

    This is an observation-uncertainty field we get for free and currently do
    not use. It belongs in the input channels and in the conformal calibration.
    """
    ds = xr.open_dataset(path)
    if "cdr_seaice_conc_stdev" not in ds:
        raise KeyError("no cdr_seaice_conc_stdev in this file")
    sd = ds["cdr_seaice_conc_stdev"].isel(time=0).values.astype(np.float32)
    return np.where((sd >= 0.0) & (sd <= 1.0), sd, np.nan)


def qa_breakdown(path: Path | str) -> dict[str, int]:
    """Count cells affected by each QA bit, for auditing a day of data."""
    ds = xr.open_dataset(path)
    if "cdr_seaice_conc_qa_flag" not in ds:
        return {}
    qa = np.nan_to_num(ds["cdr_seaice_conc_qa_flag"].isel(time=0).values,
                       nan=0).astype(np.int32)
    out = {label: int(((qa & bit) != 0).sum())
           for bit, label in QA_LABELS.items()}
    out["cells total"] = int(qa.size)
    return out


def hard_zero_next_to_ice(sic: np.ndarray, heavy: float = 0.5) -> np.ndarray:
    """Cells reading exactly zero while touching ice heavier than `heavy`.

    A physical ice edge has a gradient. An exact zero flush against 60% ice is
    a retrieval artifact, and this is the detector that first caught it -- it
    needs no QA flag, so it also works on products that ship none.
    """
    valid = np.isfinite(sic)
    zero = valid & (sic == 0.0)
    heavy_mask = valid & (sic > heavy)

    touching = np.zeros_like(heavy_mask)
    touching[1:, :] |= heavy_mask[:-1, :]
    touching[:-1, :] |= heavy_mask[1:, :]
    touching[:, 1:] |= heavy_mask[:, :-1]
    touching[:, :-1] |= heavy_mask[:, 1:]
    return zero & touching
