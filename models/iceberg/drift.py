"""Iceberg drift, Wagner, Dell & Eisenman (2017) closed form.

WDE17, *An Analytical Model of Iceberg Drift*, J. Phys. Oceanogr. 47(7),
arXiv:1610.06403, reference MATLAB at tillwagner.me/wde17.

    v_i = v_w + gamma * ( alpha * (k x v_a) + beta * v_a )

The iceberg's velocity is the surface current plus a wind-driven correction that
is partly along-wind (beta) and partly across-wind (alpha). Height cancels
exactly -- drag and Coriolis both scale linearly with it -- so geometry enters
only through the harmonic mean horizontal length S = LW/(L+W).

Why a closed form rather than integrating a momentum balance: there is nothing
to integrate. Given wind, current, latitude and size, the velocity is algebraic.
That makes it fast enough to run over every tracked berg on a laptop at sea,
which is the deployment constraint that matters here.

Three implementation traps, all of which silently produce plausible-looking
wrong answers. Each is asserted in tests/test_drift.py.

1.  DRAG COEFFICIENTS ARE SWAPPED IN THE PREPRINT TEXT. The arXiv text says
    "C_a = 0.9 and C_w = 1.3"; the reference MATLAB says the opposite, and the
    code is the one that reproduces the paper's own downstream numbers
    (gamma = 0.018, critical length L* = 765 m). Since gamma ~ sqrt(C_a/C_w),
    taking the text's assignment puts gamma 44% low. We use C_a = 1.3 (air),
    C_w = 0.9 (water).

2.  LAMBDA MUST USE |f|, NOT f. Equation (9) prints f, but Lambda is a principal
    square root of a product of two quantities both proportional to 1/f, so it
    is positive by construction. Feeding a signed Southern-Hemisphere f gives
    Lambda < 0, beta < 0, and an along-wind term pointing backwards -- which
    looks like a plausible drift, just the wrong way.

3.  ALPHA AND BETA AS PRINTED BOTH LOSE ALL PRECISION AT SMALL LAMBDA, and
    every iceberg USNIC tracks sits at Lambda < 0.07 -- so this is the normal
    operating range, not an edge case. Both reduce to differences of nearly
    equal numbers (alpha) or a bracket that decays as 2*Lambda^12 and can go
    negative in float64 (beta), and both are 0/0 at zero wind. We rewrite each
    into an algebraically identical but cancellation-free form; see the
    docstrings. No clipping and no asymptotic branch is then needed.

A note on what this model is for. For the large tabular bergs that USNIC and BYU
actually track, WDE17's own conclusion is that wind drag is negligible and the
equation reduces to v_i = v_w: they move with the surface current. So forecast
skill for the catalogue is set by the quality of the ocean-current field, not by
these coefficients. `relative_wind_forcing()` reports which regime a berg is in
so that claim is checked per berg rather than assumed.
"""

from __future__ import annotations

import numpy as np

# --- physical constants, verbatim from the WDE17 reference MATLAB ------------
OMEGA = 7.2921e-5        # Earth rotation rate, rad/s
RHO_A = 1.2              # air density, kg/m^3
RHO_W = 1027.0           # seawater density, kg/m^3
RHO_I = 850.0            # shelf-ice density, kg/m^3 (Silva et al. 2006)
C_A = 1.3                # bulk air drag coefficient   -- see trap 1
C_W = 0.9                # bulk water drag coefficient -- see trap 1

# Wind-to-water drag ratio, WDE17 eq. (7). Paper quotes 0.018.
GAMMA = float(np.sqrt(RHO_A * (RHO_W - RHO_I) / (RHO_W * RHO_I) * C_A / C_W))


def coriolis_abs(lat_deg: np.ndarray | float) -> np.ndarray | float:
    """|f| = 2 Omega sin|lat|. Always positive -- see trap 2."""
    return 2.0 * OMEGA * np.sin(np.radians(np.abs(lat_deg)))


def harmonic_length(length_m, width_m):
    """S = LW/(L+W), the only way iceberg geometry enters WDE17."""
    length_m = np.asarray(length_m, dtype=float)
    width_m = np.asarray(width_m, dtype=float)
    return length_m * width_m / (length_m + width_m)


def lambda_param(wind_speed_ms, lat_deg, length_m, width_m):
    """WDE17 eq. (9): Lambda = gamma C_w |v_a| / (pi |f| S).

    Lambda is the single dimensionless number that decides the drift regime.
    Lambda >> 1 -> wind pushes the berg along-wind; Lambda << 1 -> across-wind.
    The two asymptotes cross at Lambda = 1, where the deflection is 45 degrees.
    """
    s = harmonic_length(length_m, width_m)
    return GAMMA * C_W * np.asarray(wind_speed_ms, dtype=float) / (
        np.pi * coriolis_abs(lat_deg) * s)


def alpha(lam):
    """Across-wind coefficient, WDE17 eq. (8), in an algebraically exact form.

    The paper prints alpha = (1 - sqrt(1+4L^4)) / (2L^3), which is negative for
    all Lambda > 0; the MATLAB uses the positive form and absorbs the sign into
    the velocity assembly. Both are correct, but they must not be mixed. We
    follow the code, so `iceberg_velocity` carries the sign explicitly.

    Written as-printed, the numerator sqrt(1+4L^4) - 1 is a catastrophic
    cancellation: for the Lambda < 0.07 range every USNIC-tracked berg occupies
    it subtracts two nearly-equal numbers, and it is 0/0 at zero wind. Using
    sqrt(1+x) - 1 == x / (sqrt(1+x) + 1) removes the subtraction entirely:

        alpha = 2 * Lambda / (1 + sqrt(1 + 4 Lambda^4))

    Identical to eq. (8) in exact arithmetic, stable in float64 at every
    Lambda, and correctly zero at Lambda = 0.
    """
    lam = np.asarray(lam, dtype=float)
    return 2.0 * lam / (1.0 + np.sqrt(1.0 + 4.0 * lam ** 4))


def beta(lam):
    """Along-wind coefficient, WDE17 eq. (8), in an algebraically exact form.

    The printed bracket (1+L^4) sqrt(1+4L^4) - 3L^4 - 1 tends to 2 L^12, so in
    float64 it is pure round-off below Lambda ~ 0.08 and can evaluate negative,
    giving NaN. Multiplying by its conjugate collapses the cancellation exactly:

        (1+x) sqrt(1+4x) - (1+3x) == 4 x^3 / [ (1+x) sqrt(1+4x) + (1+3x) ]

    with x = Lambda^4, which reduces the whole coefficient to

        beta = sqrt(2) * Lambda^3 / sqrt( (1+x) sqrt(1+4x) + 1 + 3x )

    No subtraction, no underflow, no asymptotic branch, and beta(0) = 0. This
    is why LAMBDA_ASYMPTOTIC is no longer needed: it was a workaround for a
    formulation problem, and a switch point is itself a source of error -- the
    printed form was already unreliable *below* the threshold we would have set.
    """
    lam = np.asarray(lam, dtype=float)
    x = lam ** 4
    denom = (1.0 + x) * np.sqrt(1.0 + 4.0 * x) + 1.0 + 3.0 * x
    return np.sqrt(2.0) * lam ** 3 / np.sqrt(denom)


def iceberg_velocity(u_current, v_current, u_wind, v_wind,
                     lat_deg, length_m, width_m,
                     southern_hemisphere_flip: bool = True):
    """WDE17 eq. (6). Velocities in m/s eastward/northward, sizes in m.

    `lat_deg` is negative in the Southern Hemisphere.

    southern_hemisphere_flip
        Deflect the wind-driven component to the LEFT of the wind south of the
        equator, mirroring the Northern-Hemisphere right-deflection, as the
        Coriolis sign in WDE17 eq. (3)-(5) implies.

        This is NOT in the reference MATLAB. That script takes sin(|lat|) and
        assembles the velocity with a fixed clockwise rotation, so it applies
        right-of-wind deflection at every latitude -- WDE17's quantitative
        sections are Arctic, so the case was never exercised. The flip is our
        inference and is unverified against observations. It is nearly moot for
        the giants USNIC tracks (wind is ~1% of their drift) but matters for
        sub-kilometre bergs. Set False to reproduce the reference code exactly.
    """
    u_wind = np.asarray(u_wind, dtype=float)
    v_wind = np.asarray(v_wind, dtype=float)
    speed = np.hypot(u_wind, v_wind)

    lam = lambda_param(speed, lat_deg, length_m, width_m)
    a, b = alpha(lam), beta(lam)

    # +1 north, -1 south. np.sign(0) is 0, which would zero the across-wind
    # term exactly on the equator; irrelevant here but avoided for safety.
    if southern_hemisphere_flip:
        sign = np.where(np.asarray(lat_deg) < 0.0, -1.0, 1.0)
    else:
        sign = 1.0

    u_ice = u_current + GAMMA * (sign * a * v_wind + b * u_wind)
    v_ice = v_current + GAMMA * (-sign * a * u_wind + b * v_wind)
    return u_ice, v_ice


def deflection_angle_deg(lam):
    """Angle between the wind and the wind-driven drift, theta = atan(alpha/beta).

    90 degrees means pure across-wind, 0 means pure along-wind. Crosses 45
    degrees near Lambda = 1.
    """
    return np.degrees(np.arctan2(alpha(lam), beta(lam)))


def relative_wind_forcing(wind_speed_ms, current_speed_ms,
                          lat_deg, length_m, width_m):
    """WDE17 eq. (14): R = gamma sqrt(alpha^2+beta^2) |v_a| / |v_w|.

    R > 1   wind-dominated
    R < 0.1 current-dominated -- the berg effectively moves with the current

    Worth computing per berg before trusting any drift forecast: if R is small,
    the forecast's accuracy is inherited from the ocean-current product and no
    amount of drag tuning will improve it.
    """
    lam = lambda_param(wind_speed_ms, lat_deg, length_m, width_m)
    magnitude = np.hypot(alpha(lam), beta(lam))
    return GAMMA * magnitude * np.asarray(wind_speed_ms, dtype=float) / np.asarray(
        current_speed_ms, dtype=float)


def critical_length_m(wind_speed_ms, lat_deg, aspect_ratio: float = 1.5):
    """Iceberg length at which Lambda = 1, i.e. the along/across-wind crossover.

    WDE17 report L* = 765 m for |v_a| = 5.7 m/s at f = 1e-4 s^-1 with L/W = 1.5.
    Reproducing that number is one of the checks that settles the drag-
    coefficient ambiguity in trap 1.
    """
    # S = LW/(L+W) with W = L/aspect  =>  S = L/(1+aspect)
    # Lambda = 1  =>  S = gamma C_w |v_a| / (pi |f|)
    s_star = GAMMA * C_W * wind_speed_ms / (np.pi * coriolis_abs(lat_deg))
    return s_star * (1.0 + aspect_ratio)
