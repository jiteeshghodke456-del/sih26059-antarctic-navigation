"""Slice 6: RealWorld serves the router's contract from real archive files."""
import datetime as dt

import numpy as np
import pytest

from real_world import ARCHIVE, RealWorld

CYCLE = dt.date(2026, 11, 21)

pytestmark = pytest.mark.skipif(
    not (ARCHIVE / f"cmems_wav_{CYCLE}.nc").exists(),
    reason="2026-11-21 wave cycle not on disk",
)


def test_sample_fields_are_real_and_bounded():
    w = RealWorld(CYCLE)
    LA, LO = np.meshgrid(np.arange(-70, -55, 0.5), np.arange(15, 79, 0.9),
                         indexing="ij")
    s = w.sample(LA, LO, 2.0)
    sic = s["sic"][np.isfinite(s["sic"])]
    hs = s["hs"][np.isfinite(s["hs"])]
    assert len(sic) and (sic >= 0).all() and (sic <= 1).all()
    assert len(hs) and (hs >= 0).all() and (hs < 25).all()
    assert np.isfinite(s["sic"]).mean() > 0.5     # the box is mostly covered
    assert not s["beyond_horizon"]


def test_horizon_clamp_is_reported():
    w = RealWorld(CYCLE)
    s = w.sample(-66.0, 40.0, 12.0)
    assert s["beyond_horizon"] and s["day_index"] == w.n_days - 1


def test_outside_box_is_nan_not_invented():
    w = RealWorld(CYCLE)
    s = w.sample(-40.0, 100.0, 1.0)   # far outside the harvest box
    assert np.isnan(s["sic"])
