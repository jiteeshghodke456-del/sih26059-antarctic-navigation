"""Real-data drop-in for the router's World (HANDOFF_TONIGHT slice 6).

Same `.sample(lat, lon, t)` contract as `isih/sim/world.World`, but every
field comes from the archives — the router runs unchanged on real data, it is
NOT forked. Coverage is the harvest box (0–80E, 55–78S) and the 10 forecast
days of one cycle; build the Router with lattice bounds inside that box.

Field sources, per cycle date:
    sic   data/cmems_forecast_archive/cmems_siconc_<cycle>.nc  (GLO12)
    hs    data/cmems_forecast_archive/cmems_wav_<cycle>.nc     (VHM0 daily max)
    wind  data/ecmwf_wind/ecmwf_wind_<cycle>_00z.nc            (IFS 10 m, if present)

Honesty notes, enforced here rather than assumed:
- daily fields: t (days since the cycle) indexes the nearest forecast day,
  clamped to the 10-day horizon; `beyond_horizon` in the sample reports when
  the clamp fired.
- the wave model leaves VHM0 NaN under sea ice. Inside ice (sic > 0.15) hs is
  taken as 0.0 — swell is physically damped by ice cover — and
  `hs_filled_ice` reports it. Other NaNs (land, no data) stay NaN; the
  router's land mask and depth block those cells anyway.
- there is no visibility field in any of this data. sample() does not return
  one, and the weather gate must list visibility as unassessed.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
import xarray as xr

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "data" / "cmems_forecast_archive"
WIND_DIR = ROOT / "data" / "ecmwf_wind"
ICE_DAMPS_WAVES_ABOVE = 0.15


class RealWorld:
    """World built from one archived forecast cycle."""

    def __init__(self, cycle: dt.date):
        self.cycle = cycle
        ice = xr.open_dataset(ARCHIVE / f"cmems_siconc_{cycle}.nc")
        self._sic = ice["siconc"].values.astype(np.float32)
        self._lat = ice["latitude"].values
        self._lon = ice["longitude"].values
        self.n_days = self._sic.shape[0]

        wav_path = ARCHIVE / f"cmems_wav_{cycle}.nc"
        self._hs = None
        if wav_path.exists():
            wav = xr.open_dataset(wav_path)
            self._hs = wav["VHM0_dmax"].values.astype(np.float32)
            self._wav_lat = wav["latitude"].values
            self._wav_lon = wav["longitude"].values

        self._wind = None
        wind_path = WIND_DIR / f"ecmwf_wind_{cycle}_00z.nc"
        if wind_path.exists():
            w = xr.open_dataset(wind_path)
            self._wind = w
            # steps are hours since cycle 00z
            self._wind_hours = (w["step"].values / np.timedelta64(1, "h")).astype(float)

    def _interp(self, grid, lat_ax, lon_ax, lat, lon):
        """Vectorized bilinear; NaN outside the box or next to NaN cells."""
        lat = np.asarray(lat, float)
        lon = np.asarray(lon, float)
        out = np.full(np.broadcast(lat, lon).shape, np.nan, np.float32)
        inside = ((lat >= lat_ax[0]) & (lat <= lat_ax[-1])
                  & (lon >= lon_ax[0]) & (lon <= lon_ax[-1]))
        if not inside.any():
            return out
        la = np.clip(lat, lat_ax[0], lat_ax[-1])
        lo = np.clip(lon, lon_ax[0], lon_ax[-1])
        i = np.clip(np.searchsorted(lat_ax, la) - 1, 0, len(lat_ax) - 2)
        j = np.clip(np.searchsorted(lon_ax, lo) - 1, 0, len(lon_ax) - 2)
        fy = (la - lat_ax[i]) / (lat_ax[i + 1] - lat_ax[i])
        fx = (lo - lon_ax[j]) / (lon_ax[j + 1] - lon_ax[j])
        v = (grid[i, j] * (1 - fy) * (1 - fx) + grid[i, j + 1] * (1 - fy) * fx
             + grid[i + 1, j] * fy * (1 - fx) + grid[i + 1, j + 1] * fy * fx)
        out[inside] = v[inside]
        return out

    def sample(self, lat, lon, t) -> dict:
        """t is days since the cycle date (the router's convention)."""
        day = int(np.clip(round(float(np.min(t)) if np.ndim(t) else t), 0,
                          self.n_days - 1))
        beyond = (float(np.max(t)) if np.ndim(t) else t) > self.n_days - 1

        sic = self._interp(self._sic[day], self._lat, self._lon, lat, lon)

        out = {"sic": sic, "beyond_horizon": bool(beyond),
               "day_index": day, "hs_filled_ice": 0}
        if self._hs is not None:
            hs_day = min(day, self._hs.shape[0] - 1)
            hs = self._interp(self._hs[hs_day], self._wav_lat, self._wav_lon,
                              lat, lon)
            fill = np.isnan(hs) & np.isfinite(sic) & (sic > ICE_DAMPS_WAVES_ABOVE)
            hs = np.where(fill, 0.0, hs)
            out["hs"] = hs
            out["hs_filled_ice"] = int(fill.sum())
        if self._wind is not None:
            h = float(np.clip(day * 24.0 + 12.0, self._wind_hours[0],
                              self._wind_hours[-1]))
            k = int(np.argmin(np.abs(self._wind_hours - h)))
            # IFS latitude axis is descending
            u = self._interp(self._wind["u10"].values[k][::-1],
                             self._wind["latitude"].values[::-1],
                             self._wind["longitude"].values, lat, lon)
            v = self._interp(self._wind["v10"].values[k][::-1],
                             self._wind["latitude"].values[::-1],
                             self._wind["longitude"].values, lat, lon)
            out["wind_u"], out["wind_v"] = u, v
            out["wind_ms"] = np.hypot(u, v)
        return out
