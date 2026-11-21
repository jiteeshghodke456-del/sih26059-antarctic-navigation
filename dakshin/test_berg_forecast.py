"""Slice 5 checks from the handoff: stationary in still water, ~8.64 km/day in
a 0.1 m/s current, and a hard stop at the coast. Synthetic fields test the
integrator's plumbing only — validation against real USNIC positions lives in
scripts/berg_hindcast.py on real analysis currents."""
import datetime as dt

import numpy as np

from berg_forecast import (STATUS_GROUNDED, STATUS_OK, CurrentField,
                           forecast_track, great_circle_km)

START = dt.datetime(2026, 9, 2, 0, 0)
GIANT = dict(length_m=30_000.0, width_m=20_000.0)


def uniform_field(u=0.0, v=0.0, nan_east_of=None):
    lat = np.arange(-70.0, -59.9, 0.5)
    lon = np.arange(0.0, 40.1, 0.5)
    nd = 12
    uu = np.full((nd, len(lat), len(lon)), u, np.float32)
    vv = np.full((nd, len(lat), len(lon)), v, np.float32)
    if nan_east_of is not None:
        uu[:, :, lon >= nan_east_of] = np.nan
    t0 = np.datetime64(START.date()).astype("datetime64[s]").astype(float) / 86400.0
    return CurrentField(uu, vv, lat, lon, t0 + np.arange(nd) + 0.5)


def test_still_water_berg_stays_put():
    tr = forecast_track("T", -65.0, 20.0, field_=uniform_field(), start=START,
                        days=5, **GIANT)
    assert tr.status == STATUS_OK
    assert great_circle_km(tr.lats[0], tr.lons[0], tr.lats[-1], tr.lons[-1]) < 1e-6


def test_uniform_eastward_current_advects_8_64_km_per_day():
    tr = forecast_track("T", -65.0, 20.0, field_=uniform_field(u=0.1),
                        start=START, days=1, **GIANT)
    assert tr.status == STATUS_OK
    d = great_circle_km(tr.lats[0], tr.lons[0], tr.lats[-1], tr.lons[-1])
    assert abs(d - 8.64) < 0.2          # 0.1 m/s * 86400 s = 8.64 km
    assert tr.lons[-1] > tr.lons[0]     # moved east
    assert abs(tr.lats[-1] - tr.lats[0]) < 0.02


def test_coastal_berg_stops_with_grounded_flag():
    # eastward current pushing straight into a NaN (land/unknown) region
    tr = forecast_track("T", -65.0, 29.0, field_=uniform_field(u=0.5, nan_east_of=30.0),
                        start=START, days=9, **GIANT)
    assert tr.status == STATUS_GROUNDED
    assert tr.lons[-1] < 30.5           # never crossed into the unknown
    assert len(tr.times) > 1            # it did move before stopping


def test_grounding_holds_berg_on_shallow_bank():
    # v2 behaviour: a keel-deep bank under the berg means it must not advect,
    # however strong the current. Uses the real committed bathymetry.
    import numpy as np
    from berg_forecast import ASSUMED_DRAUGHT_M, BathymetryGrid

    bathy = BathymetryGrid()
    # find a real cell in the test field's area shallower than the keel
    lat_sel = (bathy.lat >= -70) & (bathy.lat <= -60)
    lon_sel = (bathy.lon >= 0) & (bathy.lon <= 40)
    depth = -bathy.elev[np.ix_(lat_sel, lon_sel)]
    cand = np.argwhere((depth > 0) & (depth < ASSUMED_DRAUGHT_M))
    assert len(cand), "no keel-deep bank in the test window — adjust window"
    i, j = cand[0]
    la = bathy.lat[lat_sel][i]
    lo = bathy.lon[lon_sel][j]
    tr = forecast_track("T", float(la), float(lo), field_=uniform_field(u=0.5),
                        start=START, days=5, bathymetry=bathy, **GIANT)
    assert tr.status == STATUS_GROUNDED
    assert len(tr.lats) == 1          # never moved

    # same berg, no bathymetry: v1 behaviour unchanged
    tr1 = forecast_track("T", float(la), float(lo), field_=uniform_field(u=0.5),
                         start=START, days=1, **GIANT)
    assert len(tr1.lats) > 1


def test_wind_forcing_R_is_small_for_giants():
    tr = forecast_track("T", -65.0, 20.0, field_=uniform_field(u=0.1),
                        start=START, days=1, **GIANT)
    assert tr.wind_forcing_R is not None and tr.wind_forcing_R < 0.1
