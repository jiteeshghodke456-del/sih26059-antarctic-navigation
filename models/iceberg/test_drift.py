"""Tests for the WDE17 iceberg drift model.

These are not plumbing tests. Each one pins a number that WDE17 publishes, or
guards a trap that produces a plausible-but-wrong drift if it regresses. The
golden alpha/beta table and the critical length are the paper's own values, so
if these pass the implementation reproduces the published model.

    prenv/bin/python -m pytest models/iceberg/test_drift.py -q
"""

import numpy as np
import pytest

from drift import (GAMMA, alpha, beta, coriolis_abs, critical_length_m,
                   deflection_angle_deg, harmonic_length, iceberg_velocity,
                   lambda_param, relative_wind_forcing)

# WDE17 table, regenerated: Lambda, alpha, beta, sqrt(a^2+b^2), theta degrees.
GOLDEN = [
    (0.01, 0.01000, 0.00000, 0.01000, 90.00),
    (0.1, 0.09999, 0.00100, 0.10000, 89.43),
    (0.5, 0.47214, 0.11470, 0.48587, 76.35),
    (1.0, 0.61803, 0.48587, 0.78615, 51.83),
    (2.0, 0.44139, 0.82943, 0.93956, 28.02),
    (5.0, 0.19604, 0.97045, 0.99005, 11.42),
    (10.0, 0.09950, 0.99253, 0.99750, 5.72),
    (100.0, 0.01000, 0.99993, 0.99998, 0.57),
]


def test_gamma_matches_paper_and_catches_swapped_drag():
    """gamma = 0.0187, not 0.0130.

    The arXiv text says C_a = 0.9, C_w = 1.3, which gives 0.01298. The
    reference MATLAB says the opposite and reproduces the paper's own stated
    gamma of 0.018. If someone swaps the constants this is the tripwire.
    """
    assert GAMMA == pytest.approx(0.018747, abs=5e-5)
    swapped = np.sqrt(1.2 * (1027.0 - 850.0) / (1027.0 * 850.0) * 0.9 / 1.3)
    assert swapped == pytest.approx(0.01298, abs=5e-5)
    assert abs(GAMMA - swapped) > 0.005, "swap must be detectable"


@pytest.mark.parametrize("lam,a_exp,b_exp,mag_exp,theta_exp", GOLDEN)
def test_golden_alpha_beta_table(lam, a_exp, b_exp, mag_exp, theta_exp):
    a, b = float(alpha(lam)), float(beta(lam))
    assert a == pytest.approx(a_exp, abs=1e-5)
    assert b == pytest.approx(b_exp, abs=1e-5)
    assert float(np.hypot(a, b)) == pytest.approx(mag_exp, abs=1e-5)
    assert float(deflection_angle_deg(lam)) == pytest.approx(theta_exp, abs=0.02)


def test_coefficients_are_finite_and_accurate_at_small_lambda():
    """Every USNIC-tracked berg sits at Lambda < 0.07, so this is the NORMAL
    operating range. As printed in the paper both coefficients are catastrophic
    cancellations here; the rewritten forms must stay finite AND match the
    analytic limits alpha -> Lambda, beta -> Lambda^3."""
    lam = np.array([0.0, 1e-6, 1e-4, 1e-3, 1e-2, 0.02, 0.05, 0.0658, 0.1])
    a, b = alpha(lam), beta(lam)
    assert np.all(np.isfinite(a)), f"non-finite alpha: {a}"
    assert np.all(np.isfinite(b)), f"non-finite beta: {b}"
    assert np.all(a >= 0.0) and np.all(b >= 0.0)

    nz = lam > 0
    assert np.allclose(a[nz], lam[nz], rtol=1e-3)
    assert np.allclose(b[nz], lam[nz] ** 3, rtol=1e-3)


def test_coefficients_are_smooth_with_no_switch_point():
    """The implementation has no asymptotic branch, so there is no threshold at
    which the value can jump. Sample densely across where a switch used to be
    and require monotonicity and smoothness."""
    lam = np.linspace(0.01, 0.5, 400)
    b = beta(lam)
    assert np.all(np.diff(b) > 0), "beta must be monotonic in Lambda"
    second = np.diff(b, 2)
    assert np.max(np.abs(second)) < 1e-4, "no kink permitted"


def test_zero_lambda_is_zero_not_nan():
    """Zero wind means Lambda = 0, which is 0/0 in the printed formulas."""
    assert float(alpha(0.0)) == 0.0
    assert float(beta(0.0)) == 0.0


def test_small_and_large_lambda_asymptotes():
    """alpha -> Lambda, beta -> Lambda^3 as Lambda -> 0;
    alpha -> 1/Lambda, beta -> 1 as Lambda -> infinity."""
    small = 1e-3
    assert float(alpha(small)) == pytest.approx(small, rel=1e-4)
    assert float(beta(small)) == pytest.approx(small ** 3, rel=1e-4)

    big = 1e3
    assert float(alpha(big)) == pytest.approx(1.0 / big, rel=1e-4)
    assert float(beta(big)) == pytest.approx(1.0, rel=1e-4)


def test_deflection_crosses_45_degrees_near_lambda_one():
    """The two asymptotes cross at Lambda = 1. Below it the wind drives the
    berg across-wind, above it along-wind."""
    assert float(deflection_angle_deg(0.2)) > 45.0
    assert float(deflection_angle_deg(5.0)) < 45.0


def test_critical_length_reproduces_765_m():
    """WDE17: L* = 765 m for |v_a| = 5.7 m/s at f = 1e-4, L/W = 1.5.

    This is the second independent check that settles the drag-coefficient
    ambiguity -- it only comes out at 765 with C_a = 1.3, C_w = 0.9.
    """
    lat = np.degrees(np.arcsin(1e-4 / (2 * 7.2921e-5)))   # f = 1e-4 s^-1
    assert float(coriolis_abs(lat)) == pytest.approx(1e-4, rel=1e-6)
    assert float(critical_length_m(5.7, lat, 1.5)) == pytest.approx(765.0, abs=3.0)


def test_lambda_is_positive_in_the_southern_hemisphere():
    """Equation (9) prints f, but Lambda must be built from |f|. A signed
    southern f gives Lambda < 0, beta < 0, and along-wind drift pointing
    backwards -- which still looks like a drift, just the wrong way."""
    lam = lambda_param(10.0, -65.0, 1000.0, 600.0)
    assert lam > 0
    assert float(lam) == pytest.approx(
        float(lambda_param(10.0, 65.0, 1000.0, 600.0)), rel=1e-12)


def test_harmonic_length_and_height_independence():
    """S = LW/(L+W) is the only route by which geometry enters. Height cancels
    exactly, so it is not even a parameter."""
    assert float(harmonic_length(1000.0, 600.0)) == pytest.approx(375.0)
    assert float(harmonic_length(70e3, 40e3)) == pytest.approx(25454.5, abs=1.0)


def test_zero_wind_gives_pure_current_advection():
    u, v = iceberg_velocity(0.12, -0.05, 0.0, 0.0, -65.0, 1000.0, 600.0)
    assert float(u) == pytest.approx(0.12)
    assert float(v) == pytest.approx(-0.05)


def test_southern_hemisphere_deflects_left_of_wind():
    """Our inferred hemisphere flip. Northward wind in the SH should push the
    berg WEST (negative u); in the NH, EAST. The reference MATLAB omits this
    and deflects right everywhere -- WDE17's quantitative work is Arctic.

    Flagged as INFERRED in drift.py; this test pins the behaviour we chose so a
    later change is deliberate rather than accidental.
    """
    # Small berg so the wind term is large enough to see clearly.
    kw = dict(length_m=200.0, width_m=120.0)
    u_s, _ = iceberg_velocity(0.0, 0.0, 0.0, 10.0, -65.0, **kw)
    u_n, _ = iceberg_velocity(0.0, 0.0, 0.0, 10.0, 65.0, **kw)
    assert float(u_s) < 0.0, "southern hemisphere should deflect left (west)"
    assert float(u_n) > 0.0, "northern hemisphere should deflect right (east)"
    assert float(u_s) == pytest.approx(-float(u_n), rel=1e-9)

    # Reproducing the reference code exactly means no flip.
    u_ref, _ = iceberg_velocity(0.0, 0.0, 0.0, 10.0, -65.0,
                                southern_hemisphere_flip=False, **kw)
    assert float(u_ref) > 0.0


def test_usnic_tracked_bergs_are_current_dominated():
    """The architectural finding: every iceberg USNIC tracks has R < 0.13, so
    v_i ~ v_w. Forecast skill for the catalogue is set by the ocean-current
    product, not by these drag coefficients.

    Values from WDE17 regime analysis at 65 S, |v_a| = 10 m/s, |v_w| = 0.1 m/s.
    """
    cases = [
        ("A23A-class giant", 70e3, 40e3, 0.030),
        ("A76-class", 30e3, 13e3, 0.084),
        ("USNIC minimum", 18.5e3, 9.3e3, 0.123),
    ]
    for name, length, width, expected_r in cases:
        r = float(relative_wind_forcing(10.0, 0.1, -65.0, length, width))
        assert r == pytest.approx(expected_r, abs=0.005), name
        assert r < 0.13, f"{name} should be current-dominated"


def test_small_bergs_are_wind_dominated():
    """Conversely, sub-kilometre bergs have R > 1 -- and those are the ones the
    hemisphere sign convention actually affects."""
    assert float(relative_wind_forcing(10.0, 0.1, -65.0, 1000.0, 600.0)) > 1.0
    assert float(relative_wind_forcing(10.0, 0.1, -65.0, 200.0, 120.0)) > 1.0


def test_two_percent_wind_rule_fails_for_antarctic_giants():
    """The '2% of wind speed' rule is an asymptotic Lambda >> 1 limit. Applying
    it to a 20 km tabular berg is a physics error a competitor may well make,
    and this test documents the size of it."""
    wind = 10.0
    u, v = iceberg_velocity(0.0, 0.0, wind, 0.0, -65.0, 20e3, 10e3)
    wind_driven = float(np.hypot(u, v))
    assert wind_driven < 0.02 * wind / 10, (
        "giant berg drift should be far below the 2% rule")


def test_vectorises_over_many_bergs():
    """One call per berg would be too slow for a laptop at sea; the catalogue
    is thousands of bergs."""
    n = 500
    lat = np.full(n, -65.0)
    length = np.full(n, 5e3)
    width = np.full(n, 3e3)
    u, v = iceberg_velocity(np.full(n, 0.1), np.zeros(n),
                            np.full(n, 8.0), np.zeros(n), lat, length, width)
    assert u.shape == (n,) and v.shape == (n,)
    assert np.all(np.isfinite(u)) and np.all(np.isfinite(v))
