"""Reproducible draws that do not depend on the NumPy version.

`np.random.default_rng(seed)` freezes the bit generator's stream but NEP 19
explicitly allows the distribution METHODS to change between releases. This
demo is built in a sandbox on numpy 2.5 / Python 3.14 and runs on the user's
WSL venv on Python 3.12. A seed that produced one world here could produce a
different one there, which would mean the recorded scenario - "on day 9 a berg
crosses the track" - simply is not true on the machine doing the demo.

blake2b is RFC 7693 and lives in the standard library. Its output is identical
on every platform and every version, forever. It is also random-access: the
parameters of item n can be drawn without drawing items 0..n-1.
"""

from __future__ import annotations

import hashlib

import numpy as np

_SCALE = 1.0 / float(1 << 64)


def uniform(seed: int, tag: str, n: int, offset: int = 0) -> np.ndarray:
    """n draws in [0, 1), stable across platforms and library versions."""
    out = np.empty(n, dtype=np.float64)
    for i in range(n):
        h = hashlib.blake2b(f"{seed}|{tag}|{offset + i}".encode(), digest_size=8)
        out[i] = int.from_bytes(h.digest(), "little") * _SCALE
    return out


def integers(seed: int, tag: str, low: int, high: int, n: int,
             offset: int = 0) -> np.ndarray:
    """n integers in [low, high)."""
    return low + np.floor(uniform(seed, tag, n, offset) * (high - low)).astype(int)


def normal(seed: int, tag: str, n: int, offset: int = 0) -> np.ndarray:
    """Box-Muller on paired uniforms, so it is as stable as `uniform`."""
    m = n + (n % 2)
    u = uniform(seed, tag, m * 2, offset)
    u1 = np.maximum(u[0::2], 2.0 ** -53)
    u2 = u[1::2]
    z = np.sqrt(-2.0 * np.log(u1)) * np.cos(2.0 * np.pi * u2)
    return z[:n]
