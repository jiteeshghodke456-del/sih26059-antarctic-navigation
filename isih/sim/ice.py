"""Sea-ice concentration with an edge that moves because the wind moved it.

The ice edge is the single most scrutinised object on this chart, so it is
built from three things that are each defensible rather than from a noise field
shaped to look right:

1.  A climatological summer edge for the 20-80E sector, retreating through the
    season. December is around 64 S in this sector, retreating to roughly 67 S
    by late February. UNVERIFIED at the level of individual longitudes.
2.  A longitudinal undulation, because the edge is not a circle - it is steered
    by bathymetry and by the standing wave pattern of the ACC.
3.  A wind-driven displacement computed from the ACTUAL meridional wind over
    the preceding two days. This is what makes the edge move for a reason: an
    on-ice wind compacts and advances it, an off-ice wind disperses it.

Concentration then ramps across the marginal ice zone rather than stepping,
because the MIZ is a real 100-200 km feature and a step edge is the fastest way
to tell an ice specialist that a field is synthetic.

The wind response is evaluated by sampling the wind field at four lags rather
than by integrating forward from t=0. That keeps the whole model directly
evaluable at an arbitrary t, which the API needs, and it is a defensible
approximation because free drift responds to wind on a timescale of hours.
"""

from __future__ import annotations

import numpy as np

from .noise import FourierField, smoothstep

# Free ice drift is about 2% of the 10 m wind (Nansen 1902). Over two days a
# sustained 15 m/s wind therefore moves the edge ~52 km, which is about half a
# degree of latitude - the right order for a synoptic event.
FREE_DRIFT_FRACTION = 0.021
MIZ_WIDTH_DEG = 3.4          # marginal ice zone width in latitude
PACK_MAX = 0.95              # concentration deep in the pack
EDGE_DEC = -63.5             # climatological edge, early December, 20-80E
EDGE_RETREAT_PER_DAY = 0.030  # deg latitude per day through the summer


class IceField:
    def __init__(self, seed: int, atmosphere):
        self.atm = atmosphere
        self.wobble = FourierField(seed, "ice", n_modes=12, lon_scale=120.0,
                                   lat_scale=60.0, alpha=1.4, drift=0.05)
        self.texture = FourierField(seed + 17, "ice", n_modes=18, lon_scale=22.0,
                                    lat_scale=9.0, alpha=1.2, drift=0.10)

    def edge_lat(self, lon, t):
        """Latitude of the 15% concentration contour."""
        lon = np.asarray(lon, dtype=float)
        base = EDGE_DEC - EDGE_RETREAT_PER_DAY * float(t)
        # The edge is not a circle: it is steered by bathymetry and by the
        # standing wave pattern of the ACC. Both are fixed features, so this
        # term is evaluated at a FIXED time. Letting it drift made the edge
        # wander for no physical reason and swamped the wind response by about
        # ten to one - a test caught it, which is what the test is for.
        undulation = 1.5 * self.wobble.value(lon, np.full_like(lon, -64.0), 0.0)

        # Wind-driven displacement: mean meridional wind over the last ~2 days,
        # sampled at four lags. Positive v (northward) pushes ice north, which
        # advances the edge toward the equator.
        v_acc = np.zeros_like(lon, dtype=float)
        lags = (0.0, 0.4, 0.8, 1.2, 1.6, 2.0)
        for lag in lags:
            _, v = self.atm.wind(lon, np.full_like(lon, base), max(0.0, float(t) - lag))
            v_acc = v_acc + v
        v_mean = v_acc / len(lags)
        # 2% of wind for 2 days, converted to degrees of latitude
        metres = FREE_DRIFT_FRACTION * v_mean * 2.0 * 86400.0
        wind_deg = metres / 111_320.0
        return base + undulation + np.clip(wind_deg, -1.6, 1.6)

    def concentration(self, lon, lat, t):
        """Sea-ice concentration, 0-1."""
        lon = np.asarray(lon, dtype=float)
        lat = np.asarray(lat, dtype=float)
        edge = self.edge_lat(lon, t)

        # South of the edge concentration rises across the MIZ to the pack value.
        south = edge - lat                       # positive when south of the edge
        c = PACK_MAX * smoothstep(0.0, MIZ_WIDTH_DEG, south)

        # Texture: floes and leads. Strongest in the MIZ, where the ice really
        # is broken, and weak deep in the pack where it is not.
        #
        # The raw Fourier field is bounded through a tanh first. A sum of
        # unit-RMS sinusoids overshoots - measured peaks here reach 2.3, not 1 -
        # and multiplying that by a concentration amplitude produced swings of
        # +/-0.39 and a profile that was not monotonic across the MIZ. An ice
        # specialist reads a non-monotonic edge instantly.
        miz_weight = np.exp(-((south - MIZ_WIDTH_DEG * 0.5) / (MIZ_WIDTH_DEG * 0.9)) ** 2)
        tex = np.tanh(0.75 * self.texture.value(lon, lat, t))
        c = c + 0.13 * miz_weight * tex

        # Coastal polynyas: katabatic winds hold open water against the coast.
        # Real, and operationally important - it is why a ship can sometimes get
        # close in when the pack offshore looks impassable. Narrow, and only
        # where there is ice to open.
        coast_band = np.exp(-((lat + 69.6) / 0.75) ** 2)
        opening = np.clip(0.5 + 0.5 * np.tanh(self.texture.value(lon * 1.7, lat, t * 0.5)), 0.0, 1.0)
        c = c - 0.5 * coast_band * opening * c

        return np.clip(c, 0.0, 1.0)

    def edge_speed_km_day(self, lon, t):
        """How fast the edge is moving, north positive. Used by the hazard
        timeline: an edge closing at 20 km/day is a different decision from a
        stationary one at the same distance."""
        h = 0.25
        a = self.edge_lat(lon, max(0.0, t - h))
        b = self.edge_lat(lon, t + h)
        return (b - a) / (2 * h) * 111.32
