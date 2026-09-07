"""Seeded, smooth, analytically differentiable random fields.

Everything in the world model needs spatially coherent randomness that is
(a) reproducible from a seed, (b) smooth enough to differentiate — the wind is
the gradient of the pressure field, so a non-differentiable pressure field would
give a wind field full of noise — and (c) evaluable at an arbitrary (x, y, t)
without a precomputed grid or a time integration, because the API must be able
to answer "what does the world look like at t?" directly.

Value or gradient noise on a hash lattice fails (b) at the lattice lines unless
you go to quintic interpolation, and even then the derivative is only C1. A
truncated Fourier series satisfies all three exactly:

    f(x, y, t) = sum_n  A_n * sin(kx_n * x + ky_n * y + w_n * t + phi_n)

with amplitudes falling as a power of wavenumber. The derivative is another
Fourier sum with the same coefficients, so gradients are exact rather than
finite-differenced. Because every mode has its own drift frequency w_n, the
field evolves without anything being stepped: t enters the phase.

The k^-alpha amplitude law is not decoration. Geophysical fields have red
spectra, and a flat spectrum looks obviously synthetic - it produces fields with
no large-scale organisation, all texture and no weather.
"""

from __future__ import annotations

import numpy as np

from .hashing import integers, uniform

# A prime multiplier per stream so that two fields asking for the same seed do
# not get identical phases. Deriving stream seeds by addition would make
# neighbouring streams correlated.
_STREAM = {
    "pressure": 1_000_003,
    "current": 2_000_003,
    "ice": 3_000_003,
    "sst": 4_000_029,
    "moisture": 5_000_011,
    "eddy": 6_000_011,
}


class FourierField:
    """A smooth scalar field on (lon, lat, t), with exact spatial gradients.

    Units: lon and lat in degrees, t in days. Output is dimensionless in
    roughly [-1, 1]; callers scale it into physical units.
    """

    def __init__(self, seed: int, stream: str, n_modes: int = 24,
                 lon_scale: float = 60.0, lat_scale: float = 22.0,
                 alpha: float = 1.6, drift: float = 0.35,
                 normalize: str = "value"):
        s = seed * 7919 + _STREAM[stream]
        # Wavenumbers: integer harmonics of the domain scale, so the field is
        # organised at the size of real synoptic systems rather than at pixel
        # scale. n=1 modes carry the most amplitude.
        n = integers(s, "n", 1, 6, n_modes)
        m = integers(s, "m", 1, 5, n_modes)
        self.kx = 2 * np.pi * n / lon_scale
        self.ky = 2 * np.pi * m / lat_scale
        k = np.hypot(self.kx, self.ky)
        self.amp = (k / k.min()) ** (-alpha)
        if normalize == "grad":
            # Normalise so the RMS gradient magnitude is 1 per degree. This is
            # the useful normalisation whenever the field will be
            # differentiated -- the pressure field's job is to produce a wind
            # of a given strength, and wind depends on the gradient, not on the
            # anomaly amplitude. Normalising by value instead (the obvious
            # choice) makes the resulting gradient scale with wavenumber, which
            # is how a plausible-looking pressure field produces a 35 m/s gale
            # over the entire Southern Ocean.
            gk = self.amp * k
            self.amp /= np.sqrt((gk ** 2).sum() / 2.0)
        else:
            self.amp /= np.sqrt((self.amp ** 2).sum() / 2.0)   # unit RMS value
        self.phi = 2 * np.pi * uniform(s, "phase", n_modes)
        # Eastward phase speed: Southern Ocean synoptic systems propagate east.
        # Scaling drift by 1/k makes long waves slower than short ones, which is
        # the right sense for Rossby-like propagation.
        jitter = 0.6 + 0.8 * uniform(s, "drift", n_modes)
        self.w = drift * (2 * np.pi) * jitter / np.maximum(k, 1e-6) * k.min()

    def _phase(self, lon, lat, t):
        lon = np.asarray(lon, dtype=float)
        lat = np.asarray(lat, dtype=float)
        return (self.kx[:, None] * lon.ravel()[None, :]
                + self.ky[:, None] * lat.ravel()[None, :]
                + self.w[:, None] * float(t)
                + self.phi[:, None])

    def value(self, lon, lat, t):
        shape = np.asarray(lon, dtype=float).shape
        ph = self._phase(lon, lat, t)
        v = (self.amp[:, None] * np.sin(ph)).sum(axis=0)
        return v.reshape(shape)

    def grad(self, lon, lat, t):
        """(d/dlon, d/dlat) — exact, not finite-differenced."""
        shape = np.asarray(lon, dtype=float).shape
        ph = self._phase(lon, lat, t)
        c = self.amp[:, None] * np.cos(ph)
        dlon = (self.kx[:, None] * c).sum(axis=0).reshape(shape)
        dlat = (self.ky[:, None] * c).sum(axis=0).reshape(shape)
        return dlon, dlat


def smoothstep(edge0: float, edge1: float, x):
    """Hermite step, C1 continuous. Used wherever a field must transition
    between regimes (ice edge, frontal jets) without a visible seam."""
    t = np.clip((np.asarray(x, dtype=float) - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)
