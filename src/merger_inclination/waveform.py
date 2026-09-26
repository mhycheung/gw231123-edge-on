"""Surrogate evaluation, spin-weighted harmonics and the mode sum."""

from dataclasses import dataclass
from functools import lru_cache
from math import comb, factorial

import numpy as np
from scipy.interpolate import CubicSpline

# Solar mass in seconds, G M_sun / c^3. Source: LAL (lal.MTSUN_SI), [@lalsuite]; asserted below.
import lal
MTSUN_SI = lal.MTSUN_SI
assert abs(MTSUN_SI - 4.925490947641267e-06) < 1e-15, MTSUN_SI


def sYlm(s, l, m, theta, phi):
    """Spin-weighted spherical harmonic, vectorised; Goldberg et al. (1967) sum.

    Same convention as gwtools.harmonics.sYlm (the one gwsurrogate uses); tested in
    src/tests/test_harmonics.py.
    """
    theta, phi = np.broadcast_arrays(np.asarray(theta, float), np.asarray(phi, float))
    c, sn = np.cos(theta / 2), np.sin(theta / 2)
    pref = (-1) ** m * np.sqrt(factorial(l + m) * factorial(l - m) * (2 * l + 1)
                               / (4 * np.pi * factorial(l + s) * factorial(l - s)))
    tot = np.zeros(theta.shape)
    for r in range(0, l - s + 1):
        k = r + s - m
        if k < 0 or k > l + s:
            continue
        p = 2 * r + s - m  # power of cot(theta/2)
        tot = tot + comb(l - s, r) * comb(l + s, k) * (-1) ** (l - r - s) \
            * sn ** (2 * l - p) * c ** p
    return pref * tot * np.exp(1j * m * phi)


@lru_cache(maxsize=None)
def load_surrogate(name):
    import gwsurrogate
    return gwsurrogate.LoadSurrogate(name)


@dataclass
class Waveform:
    t: np.ndarray          # times, M
    modes: list            # [(l, m), ...]
    H: np.ndarray          # (n_t, n_modes) complex mode data, units of M/r
    q_copr: np.ndarray     # (4, n_t) coprecessing -> inertial quaternions
    orbphase: np.ndarray   # coprecessing-frame orbital phase
    f_ref_geom: float      # f_ref in cycles/M
    t_ref: float           # reference epoch (q_copr = identity), M; grid resolution
    model: str

    def __post_init__(self):
        self._spl = CubicSpline(self.t, self.H, axis=0)
        self._qspl = CubicSpline(self.t, self.q_copr, axis=1)

    def modes_at(self, t, nu=0):
        """Mode vector (or its nu-th time derivative) at time(s) t."""
        return self._spl(t, nu)

    def quat_at(self, t):
        q = self._qspl(t)
        return q / np.linalg.norm(q, axis=0)

    def ylm_matrix(self, theta, phi):
        """(n_dir, n_modes) matrix of -2Y_lm at the given directions."""
        theta, phi = np.atleast_1d(theta), np.atleast_1d(phi)
        return np.stack([sYlm(-2, l, m, theta, phi) for l, m in self.modes], axis=-1)

    def strain(self, theta, phi, t=None):
        """h = h_+ - i h_x along (theta, phi): on the time grid, or at time(s) t."""
        Y = self.ylm_matrix(theta, phi)[0]
        H = self.H if t is None else self.modes_at(t)
        return H @ Y


def evaluate(p, model="NRSur7dq4v2", dt=0.1, f_low=0.0):
    """Evaluate `model` for parameter dict p (see params.py), geometric units."""
    m1, m2 = p["mass_1"], p["mass_2"]
    if m1 < m2:
        raise ValueError("mass_1 must be the heavier mass (LAL convention)")
    M = m1 + m2
    chiA = [p["spin_1x"], p["spin_1y"], p["spin_1z"]]
    chiB = [p["spin_2x"], p["spin_2y"], p["spin_2z"]]
    f_ref_geom = p["f_ref"] * M * MTSUN_SI
    sur = load_surrogate(model)
    t, h, dyn = sur(m1 / m2, chiA, chiB, dt=dt, f_low=f_low, f_ref=f_ref_geom,
                    precessing_opts={"return_dynamics": True})
    modes = sorted(h)
    H = np.stack([h[k] for k in modes], axis=-1)
    orb = dyn["orbphase"]
    q_copr = np.asarray(dyn["q_copr"])
    # t_ref: the reference epoch, where the coprecessing frame equals the inertial frame
    # (q_copr = identity, gwsurrogate's init_quat default). An estimate from d(orbphase)/dt =
    # pi f_ref missed it by 3-11 M for precessing samples (t02 S1, subcontext/S1_tref.md).
    dist = np.linalg.norm(q_copr - np.array([[1.0], [0.0], [0.0], [0.0]]), axis=0)
    t_ref = float(t[int(np.argmin(dist))])
    return Waveform(t=t, modes=modes, H=H, q_copr=q_copr, orbphase=orb,
                    f_ref_geom=f_ref_geom, t_ref=t_ref, model=model)
