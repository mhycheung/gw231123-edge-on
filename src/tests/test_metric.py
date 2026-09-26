"""Unit tests of mismatch_metric (t03). The S1 controls on real points are in
tasks/t03-mismatch-volume/S1/controls.py; these test the algebra and the waveform plumbing.
"""

import warnings

import numpy as np
import pytest

from mismatch_metric import defaults as D
from mismatch_metric.metric import (Setup, _dsignal_dpsi, _fd_plan, _scaled_logdet,
                                    log_prior_int, planck_start, polarizations, profile,
                                    signal, valid)

X_ML = np.array([299.67087250168464, 0.9098799950223562, 0, 0, 0, 0, 0, 0,
                 1.1227292632983898, 1.9914967391382514, 2.319660241513669, 0.0])


@pytest.fixture(scope="module")
def S():
    warnings.simplefilter("ignore")
    return Setup()


def random_spd(n, rng):
    A = rng.normal(size=(n, n))
    return A @ A.T + n * np.eye(n)


def test_profile_pivot_independent():
    """g^theta does not depend on which of iota, phi_ref is replaced by iota_Q(0)."""
    rng = np.random.default_rng(0)
    g = random_spd(12, rng)
    grad = np.r_[rng.normal(size=10), 0, 0]
    grad[8], grad[9] = 0.8, 0.6
    a = profile(g, grad)["g_theta"]
    grad2 = grad.copy()
    grad2[8], grad2[9] = 0.6, 0.8        # pivot switches to phi_ref
    b_piv = profile(g, grad2)["pivot"]
    assert b_piv == D.I_PHI
    # the same theta chart built directly: g^theta = [J g^-1 J^T]^-1
    J = np.zeros((9, 12))
    J[:8, :8] = np.eye(8)
    J[8] = grad
    direct = np.linalg.inv(J @ np.linalg.inv(g) @ J.T)
    assert np.allclose(a, direct, rtol=1e-9, atol=1e-12)
    J[8] = grad2
    assert np.allclose(profile(g, grad2)["g_theta"],
                       np.linalg.inv(J @ np.linalg.inv(g) @ J.T), rtol=1e-9, atol=1e-12)


def test_logdet_independent_of_intrinsic_gradient():
    """det g^theta depends on d iota_Q0 / d(iota, phi_ref) only (a shear has unit Jacobian)."""
    rng = np.random.default_rng(1)
    g = random_spd(12, rng)
    grad = np.r_[rng.normal(size=8), 0.9, 0.3, 0, 0]
    ld1 = _scaled_logdet(profile(g, grad)["g_theta"])[1]
    grad[:8] = rng.normal(size=8) * 5
    ld2 = _scaled_logdet(profile(g, grad)["g_theta"])[1]
    assert abs(ld1 - ld2) < 1e-9
    grad[8] = 0.45                          # a change in d iota_Q0 / d iota must matter
    assert abs(_scaled_logdet(profile(g, grad)["g_theta"])[1] - ld1) > 0.1


def test_profile_singular_nuisance_block():
    """Degenerate phi_ref, psi (face-on): the pseudo-inverse gives a finite g^theta."""
    rng = np.random.default_rng(2)
    B = rng.normal(size=(12, 11))
    B[:, 10] = B[:, 9]                    # psi direction = phi_ref direction
    g = B @ B.T
    g[:9, :9] += np.eye(9)
    grad = np.r_[np.zeros(8), 1.0, 0.0, 0, 0]
    gt = profile(g, grad)["g_theta"]
    assert np.all(np.isfinite(gt)) and np.all(np.linalg.eigvalsh(gt) > 0)


def test_rebuilt_fd_equals_lal(S):
    """Our padding, FFT and epoch (_td_to_fd) applied to SimInspiralTD reproduce
    SimInspiralFD, so the only change in polarizations() is the choice of tapers."""
    import lal
    import lalsimulation as lalsim
    from mismatch_metric.metric import _APPROX, _td_to_fd, masses
    x = X_ML
    m1, m2 = masses(x[0], x[1])
    args = (m1 * lal.MSUN_SI, m2 * lal.MSUN_SI, *x[2:8], 1e9 * lal.PC_SI, x[8], x[9], 0, 0, 0)
    hp, hc = lalsim.SimInspiralTD(*args, D.DELTA_T, 0.0, D.F_REF, lal.CreateDict(), _APPROX)
    a, b, ep = _td_to_fd(S, hp, hc)
    fp, fc = lalsim.SimInspiralFD(*args, S.df, 0.0, D.F_MAX, D.F_REF, lal.CreateDict(), _APPROX)
    assert abs(ep - float(fp.epoch)) < 1e-9
    assert np.max(np.abs(a - fp.data.data)) < 1e-6 * np.max(np.abs(fp.data.data))


def test_psi_derivative_exact(S):
    pols = polarizations(S, X_ML[:10])
    psi, h = 0.7, 1e-6
    fd = (signal(S, pols, psi + h) - signal(S, pols, psi - h)) / (2 * h)
    an = _dsignal_dpsi(S, pols, psi)
    assert np.max(np.abs(fd - an)) < 1e-6 * np.max(np.abs(an))


def test_planck_start():
    t = np.linspace(-1, 2, 3001)
    w = planck_start(t, 0.0, 1.0)
    assert w[t <= 0].max() == 0 and w[t >= 1].min() == 1
    assert np.all(np.diff(w) >= 0) and abs(planck_start(np.array([0.5]), 0, 1)[0] - 0.5) < 1e-12


def test_fd_plan_domain():
    x = X_ML.copy()
    x[1] = 0.999
    offs, w, h, flag = _fd_plan(x, 1, 1e-3, 4)
    assert flag == "onesided" and all(x[1] + o <= 1 for o in offs)
    x = X_ML.copy()
    x[2:5] = [0.98, 0.0, 0.1]
    offs, w, h, flag = _fd_plan(x, 2, 2e-2, 4)
    for o in offs:
        xx = x.copy()
        xx[2] += o
        assert valid(xx)
    # second-order one-sided weights differentiate a quadratic exactly
    f = lambda v: 3 * v ** 2 + 2 * v      # noqa: E731
    d = sum(wi * f(x[2] + o) for o, wi in zip(offs, w)) / h
    assert abs(d - (6 * x[2] + 2)) < 1e-9


def test_log_prior_jacobian():
    """M/(1+q)^2 is the Jacobian of (m1, m2) -> (M, q); check by finite differences."""
    M, q, e = 300.0, 0.8, 1e-6
    m = lambda M, q: np.array([M / (1 + q), M * q / (1 + q)])  # noqa: E731
    J = np.column_stack([(m(M + e, q) - m(M - e, q)) / (2 * e), (m(M, q + e) - m(M, q - e)) / (2 * e)])
    x = np.array([M, q, 0.3, 0, 0, 0, 0.5, 0, 1, 1, 1, 0])
    base = log_prior_int(x) + np.log(4 * np.pi * 0.3 ** 2 * D.A_MAX) \
        + np.log(4 * np.pi * 0.5 ** 2 * D.A_MAX)
    assert abs(base - np.log(abs(np.linalg.det(J)))) < 1e-8
