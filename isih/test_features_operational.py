"""Slice 2 checks: the operational channel builder places data exactly as
training's build_channels did, and structurally cannot leak future data.

Synthetic fixtures here test code plumbing only — the model is never scored
on synthetic data (see hard rules in HANDOFF_TONIGHT).
"""
import numpy as np
import pytest

from features import N_CHANNELS, N_HISTORY, build_channels_operational, iiee_km2


def _sample():
    ny, nx = 6, 5
    rng = np.random.default_rng(7)
    fc = rng.uniform(0, 1, (ny, nx)).astype(np.float32)
    an = rng.uniform(0, 1, (ny, nx)).astype(np.float32)
    hist = rng.uniform(0, 1, (N_HISTORY, ny, nx)).astype(np.float32)
    return fc, an, hist


def test_channel_layout_matches_training():
    fc, an, hist = _sample()
    x, valid = build_channels_operational(fc, an, hist, 20261121)
    assert x.shape == (1, N_CHANNELS, *fc.shape)
    np.testing.assert_array_equal(x[0, 0], fc)           # forecast at target
    for k in range(N_HISTORY):                           # obs newest first
        np.testing.assert_array_equal(x[0, 1 + k], hist[k])
    np.testing.assert_array_equal(x[0, 8], an - hist[0])  # innovation at t
    assert valid.all()


def test_nan_fill_and_valid_mask():
    fc, an, hist = _sample()
    fc[0, 0] = np.nan
    an[1, 1] = np.nan
    hist[0, 2, 2] = np.nan
    x, valid = build_channels_operational(fc, an, hist, 20261121)
    assert x[0, 0, 0, 0] == 0.0                   # NaN→0, training convention
    assert not valid[1, 1] and not valid[2, 2]    # either side missing → invalid
    assert valid[0, 0]                             # forecast NaN doesn't kill valid[t]
    np.testing.assert_array_equal(x[0, 11], valid.astype(np.float32))
    assert np.isfinite(x).all()


def test_history_length_enforced():
    fc, an, hist = _sample()
    with pytest.raises(ValueError, match="history"):
        build_channels_operational(fc, an, hist[:3], 20261121)


def test_iiee_counts_disagreement_area():
    pred = np.array([[0.2, 0.0], [0.2, 0.2]])
    truth = np.array([[0.2, 0.2], [0.0, 0.2]])
    mask = np.ones((2, 2), bool)
    # two cells disagree at the 15% threshold -> 2 * 625 km2
    assert iiee_km2(pred, truth, mask) == 1250.0
    mask[0, 1] = False
    assert iiee_km2(pred, truth, mask) == 625.0
