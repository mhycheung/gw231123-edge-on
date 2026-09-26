"""Waveform, inner product, the metric g^x, the chart change to iota_Q(0), the profiled metric
g^theta, the prior density and the score s (plan.md of t03, "Design").

The waveform and the detector response reproduce bilby's `lal_binary_black_hole` with
`LALCBCWaveformGenerator` and `Interferometer.get_detector_response` (bilby 2.6.0,
bilby/gw/source.py `_base_lal_cbc_fd_waveform`, bilby/gw/detector/interferometer.py), without
calibration unless `calibration=` is given (S1 check (a) only).
"""

import warnings

import h5py
import lal
import lalsimulation as lalsim
import numpy as np

from merger_inclination.frames import line_of_sight
from merger_inclination.inclination import iota_Q
from merger_inclination.waveform import evaluate

from . import defaults as D

_APPROX = lalsim.GetApproximantFromString(D.APPROXIMANT)


class Setup:
    """Frequencies, noise weights, sky position and detector geometry, fixed per run."""

    def __init__(self, pe=D.PE_FILE, sky_index=D.ML_INDEX):
        self.df = 1.0 / D.DURATION
        f_full = np.arange(0, D.SAMPLING_FREQUENCY / 2 + self.df / 2, self.df)
        self.n_full = len(f_full)
        self.bounds = (f_full >= D.F_MIN_WF) & (f_full <= D.F_MAX)  # waveform band (bilby)
        self.mask = (f_full >= D.F_MIN) & (f_full <= D.F_MAX)        # likelihood band
        self.f = f_full[self.mask]
        self.f_full = f_full
        with h5py.File(pe, "r") as fh:
            g = fh[D.LABEL]
            psd = {d: g["psds/" + d][()] for d in D.DETECTORS}
            ps = g["posterior_samples"][()]
            self.sky = {k: float(ps[k][sky_index]) for k in ("ra", "dec", "geocent_time")}
        self.start_time = D.TRIGGER_TIME + D.POST_TRIGGER - D.DURATION
        gmst = lal.GreenwichMeanSiderealTime(self.sky["geocent_time"])
        self.gmst = gmst
        self.det, self.dt, self.w = {}, {}, []
        for d in D.DETECTORS:
            fr, S = psd[d][:, 0], psd[d][:, 1]
            assert np.allclose(fr, f_full[: len(fr)]), d
            S_masked = S[self.mask[: len(S)]]
            assert len(S_masked) == len(self.f) and np.all(S_masked > 0)
            self.det[d] = lal.cached_detector_by_prefix[d]
            delay = lal.TimeDelayFromEarthCenter(self.det[d].location, self.sky["ra"],
                                                 self.sky["dec"], self.sky["geocent_time"])
            self.dt[d] = self.sky["geocent_time"] - self.start_time + delay
            self.w.append(4 * self.df / S_masked)
        self.w = np.concatenate(self.w)

    def antenna(self, psi):
        """{det: (F+, Fx)} at polarization angle psi."""
        return {d: lal.ComputeDetAMResponse(self.det[d].response, self.sky["ra"],
                                            self.sky["dec"], psi, self.gmst)
                for d in D.DETECTORS}

    def inner(self, a, b):
        """<a, b> = 4 Re sum_D int a_D b_D^* / S_D df over [F_MIN, F_MAX] (real, symmetric)."""
        return float(np.sum(self.w * (np.conj(a) * b).real))


def masses(M, q):
    m1 = M / (1 + q)
    return m1, q * m1


def _td_to_fd(S, hp, hc):
    """LAL's XLALSimInspiralFD after the time-domain call: pad at the start to 1/(df dt)
    samples, FFT times dt; epoch moves back by the padding. Returns (h+, hx, epoch)."""
    dt = hp.deltaT
    n_chirp = int(round(1.0 / (S.df * dt)))
    n = hp.data.length
    if n > n_chirp:
        raise ValueError("waveform longer than the data segment")
    epoch = float(hp.epoch) - (n_chirp - n) * dt
    out = []
    for h in (hp, hc):
        a = np.zeros(n_chirp)
        a[n_chirp - n:] = h.data.data
        out.append(np.fft.rfft(a) * dt)
    return out[0], out[1], epoch


def planck_start(t, t_a, T):
    """Planck taper rising from 0 at t_a to 1 at t_a + T (LAL's TAPER_START form, continuous)."""
    tau = (np.asarray(t, float) - t_a) / T
    w = np.zeros_like(tau)
    w[tau >= 1] = 1.0
    m = (tau > 0) & (tau < 1)
    z = 1 / tau[m] + 1 / (tau[m] - 1)
    w[m] = 0.5 * (1 - np.tanh(z / 2))   # = 1 / (exp(z) + 1), without overflow
    return w


def polarizations(S, x, distance=1000.0, tapers=D.TAPERS_M, lal_fd=False):
    """(h+, hx) on the likelihood band, bilby's time convention (t = 0 at geocent_time).

    x: the first 10 coordinates (M, q, chi1 xyz, chi2 xyz, iota, phi_ref); distance in Mpc.
    lal_fd=True: LAL's SimInspiralFD as bilby calls it (the PE waveform: ChooseTDWaveform, LAL
    TAPER_START from the first sample to the second extremum of each polarisation, pad, FFT).
    Otherwise: ChooseTDWaveform, then tapers fixed in continuous time, in units of M:
    tapers = (T_start, t_a, t_b): a Planck taper over the first T_start after the start
    (-4300 M), and a cos^2 taper to zero between t_a and t_b after t = 0. LAL's taper ends at a
    sample index and the series ends abruptly; both make the waveform jump as the parameters
    change (S1/controls.md). tapers=None gives the untapered series.
    """
    M, q = x[0], x[1]
    if q > 1:
        raise ValueError("q = m2/m1 must be <= 1")
    m1, m2 = masses(M, q)
    args = (m1 * lal.MSUN_SI, m2 * lal.MSUN_SI, *x[2:5], *x[5:8], distance * 1e6 * lal.PC_SI,
            x[8], x[9], 0.0, 0.0, 0.0)
    if lal_fd:
        hp, hc = lalsim.SimInspiralFD(*args, S.df, D.F_MIN_WF, D.F_MAX, D.F_REF,
                                      lal.CreateDict(), _APPROX)
        pols = []
        for h in (hp, hc):
            a = np.zeros(S.n_full, complex)
            n = min(len(h.data.data), S.n_full)
            a[:n] = h.data.data[:n]
            pols.append(a)
        epoch = float(hp.epoch)
    else:
        hp, hc = lalsim.SimInspiralChooseTDWaveform(*args, D.DELTA_T, D.F_MIN_WF, D.F_REF,
                                                    lal.CreateDict(), _APPROX)
        if tapers is not None:
            t = float(hp.epoch) + np.arange(hp.data.length) * hp.deltaT
            Ms = M * lal.MTSUN_SI
            T0, ta, tb = tapers[0] * Ms, tapers[1] * Ms, tapers[2] * Ms
            w = planck_start(t, float(hp.epoch), T0)
            w *= np.where(t <= ta, 1.0,
                          np.where(t >= tb, 0.0, np.cos(0.5 * np.pi * (t - ta) / (tb - ta)) ** 2))
            hp.data.data = hp.data.data * w
            hc.data.data = hc.data.data * w
        a, b, epoch = _td_to_fd(S, hp, hc)
        pols = [a[:S.n_full], b[:S.n_full]]
    out = []
    shift = 1 / S.df + epoch
    for a in pols:
        a = a * S.bounds
        a[S.bounds] *= np.exp(-2j * np.pi * shift * S.f_full[S.bounds])
        out.append(a[S.mask])
    return out


def signal(S, pols, psi, t_c=0.0, calibration=None):
    """Network signal vector (H1 then L1 on the likelihood band)."""
    hp, hc = pols
    F = S.antenna(psi)
    out = []
    for d in D.DETECTORS:
        s = (F[d][0] * hp + F[d][1] * hc) * np.exp(-2j * np.pi * S.f * (S.dt[d] + t_c))
        if calibration is not None:
            s = s * calibration[d](S.f)
        out.append(s)
    return np.concatenate(out)


def _dsignal_dpsi(S, pols, psi, t_c=0.0):
    """Exact: F_{+,x}(psi) = A cos(2 psi + a), so dF/dpsi = 2 F(psi + pi/4)."""
    return 2 * signal(S, pols, psi + np.pi / 4, t_c)


def valid(x):
    """Inside the waveform's and the prior's domain: q <= 1, |chi_i| <= A_MAX."""
    return (x[1] <= D.Q_MAX and np.linalg.norm(x[2:5]) <= D.A_MAX
            and np.linalg.norm(x[5:8]) <= D.A_MAX)


_CENTRAL = {2: ((-1.0, 1.0), (-0.5, 0.5)),
            4: ((-2.0, -1.0, 1.0, 2.0), (1 / 12, -8 / 12, 8 / 12, -1 / 12))}


def _fd_plan(x, k, h, order=2):
    """Offsets and weights of the difference for coordinate k: central (order 2 or 4) unless a
    stencil point leaves the domain; then one-sided, second order, towards the interior (q
    down; a spin component towards 0), halving h until valid.

    Returns (offsets, weights, h, flag); the derivative is sum_j w_j f(x + o_j e_k) / h.
    """
    def ok(offs):
        for o in offs:
            xx = np.array(x, float)
            xx[k] += o
            if not valid(xx):
                return False
        return True

    u, w = _CENTRAL[order]
    if ok([h * o for o in u]):
        return tuple(h * o for o in u), w, h, ""
    s = -1.0 if (k == 1 or x[k] > 0) else 1.0
    for _ in range(8):
        offs = (0.0, s * h, 2 * s * h)
        if ok(offs):
            return offs, (-1.5 * s, 2.0 * s, -0.5 * s), h, "onesided"
        h *= 0.5
    raise ValueError(f"no valid stencil for coordinate {k}")


def _iota_q0(p_int, iota, phi, model, wf=None):
    if wf is None:
        wf = evaluate(p_int, model=model, dt=D.SUR_DT)
    return float(iota_Q(wf, line_of_sight(iota, phi), 0.0)), wf


def _pdict(x):
    m1, m2 = masses(x[0], x[1])
    return {"mass_1": m1, "mass_2": m2, "spin_1x": x[2], "spin_1y": x[3], "spin_1z": x[4],
            "spin_2x": x[5], "spin_2y": x[6], "spin_2z": x[7], "f_ref": D.F_REF}


def chi_p(x):
    q = x[1]
    return max(np.hypot(x[2], x[3]), (4 * q + 3) / (4 + 3 * q) * q * np.hypot(x[5], x[6]))


def log_prior_int(x):
    """log of the PE prior density on (M, q, chi1, chi2), up to one constant.

    Uniform in detector-frame (m1, m2): Jacobian |d(m1, m2)/d(M, q)| = M / (1 + q)^2.
    Each spin: a ~ U(0, A_MAX), isotropic direction: 1 / (4 pi a^2 A_MAX) per Cartesian volume.
    """
    a1, a2 = np.linalg.norm(x[2:5]), np.linalg.norm(x[5:8])
    return (np.log(x[0]) - 2 * np.log1p(x[1])
            - np.log(4 * np.pi * a1 ** 2 * D.A_MAX) - np.log(4 * np.pi * a2 ** 2 * D.A_MAX))


def _derivative(f, x, k, h, order, f0=None):
    offs, wts, h, flag = _fd_plan(x, k, h, order)
    acc = 0.0
    for o, wgt in zip(offs, wts):
        if o == 0.0:
            v = f0 if f0 is not None else f(x)
        else:
            xk = x.copy()
            xk[k] += o
            v = f(xk)
        acc = acc + wgt * v
    return acc / h, h, flag


def _metric_from(S, h0, dh):
    n = S.inner(h0, h0)
    m = len(dh)
    G = np.array([[S.inner(dh[i], dh[j]) for j in range(m)] for i in range(m)])
    a = np.array([S.inner(h0, dh[i]) for i in range(m)])
    return (G - np.outer(a, a) / n) / n, G / n


def metric_x(S, x, delta=D.FD_DELTA, model=D.APPROXIMANT, pilot=D.STEPS,
             k_steps=D.K_STEPS, h_max=D.STEP_MAX):
    """g^x (12 x 12), the unprojected metric, and grad iota_Q(0) (12) at x (12 coordinates).

    Waveform derivatives: a pilot second-order pass with steps `pilot` gives the projected
    diagonal g_kk; the final step is h_k = delta / sqrt(g_kk) (at most h_max), so that one step
    changes the unit signal by `delta`, with a fourth-order central stencil. This keeps the
    error from the waveform's small jumps (S1/controls.md) below ~0.3 %.
    iota_Q(0) derivatives: fixed small steps k_steps, second order (the surrogate dynamics are
    smooth). Returns a dict with g_x, g_x_unproj, grad_iq0, iota_Q0, steps, flags, h0.
    """
    x = np.asarray(x, float)
    psi, t_c = x[D.I_PSI], x[D.I_TC]
    pols0 = polarizations(S, x[:10])
    h0 = signal(S, pols0, psi, t_c)
    hfun = lambda xx: signal(S, polarizations(S, xx[:10]), psi, t_c)  # noqa: E731
    flags = []
    # pilot
    dh_p = np.array([_derivative(hfun, x, k, pilot[k], 2, h0)[0] for k in range(10)])
    g_p, _ = _metric_from(S, h0, dh_p)
    steps = np.minimum(delta / np.sqrt(np.abs(np.diag(g_p))), h_max)
    dh = np.zeros((12, len(h0)), complex)
    used = np.zeros(10)
    for k in range(10):
        dh[k], used[k], flag = _derivative(hfun, x, k, steps[k], 4, h0)
        if flag:
            flags.append(f"{flag}:{D.X_NAMES[k]}")
    dh[D.I_PSI] = _dsignal_dpsi(S, pols0, psi, t_c)
    dh[D.I_TC] = -2j * np.pi * np.tile(S.f, len(D.DETECTORS)) * h0
    g, g_unproj = _metric_from(S, h0, dh)
    # iota_Q(0) and its gradient
    p0 = _pdict(x)
    iq0, wf0 = _iota_q0(p0, x[8], x[9], model)

    def iq(xx):
        if np.array_equal(xx[:8], x[:8]):   # iota, phi_ref: only the line of sight moves
            return _iota_q0(p0, xx[8], xx[9], model, wf=wf0)[0]
        return _iota_q0(_pdict(xx), xx[8], xx[9], model)[0]

    grad = np.zeros(12)
    for k in range(10):
        grad[k], _, flag = _derivative(iq, x, k, k_steps[k], 2, iq0)
        if flag:
            flags.append(f"K_{flag}:{D.X_NAMES[k]}")
    if min(x[8], np.pi - x[8]) < 2 * used[8]:
        flags.append("iota_near_pole")
    return {"g_x": g, "g_x_unproj": g_unproj, "grad_iq0": grad, "iota_Q0": iq0,
            "steps": used, "flags": flags, "h_norm2": S.inner(h0, h0), "h0": h0}


def _scaled_logdet(g):
    e = np.sqrt(np.abs(np.diag(g)))
    gs = g / np.outer(e, e)
    sign, ld = np.linalg.slogdet(gs)
    return sign, ld + 2 * np.sum(np.log(e)), np.linalg.cond(gs)


def profile(g_x, grad, rcond=D.PINV_RCOND):
    """Chart change to theta = (M, q, chi1, chi2, iota_Q(0)) and Schur complement.

    The pivot (iota or phi_ref, whichever iota_Q(0) depends on more) is replaced by iota_Q(0);
    the other two nuisances are psi, t_c. g^theta does not depend on the pivot: it is the metric
    minimised over the level set of theta, which is the same set in either chart.
    """
    pivot = D.I_IOTA if abs(grad[D.I_IOTA]) >= abs(grad[D.I_PHI]) else D.I_PHI
    other = D.I_PHI if pivot == D.I_IOTA else D.I_IOTA
    K = np.eye(12)
    K[pivot] = grad
    Ki = np.linalg.inv(K)
    gy = Ki.T @ g_x @ Ki
    th = list(range(8)) + [pivot]
    nu = [other, D.I_PSI, D.I_TC]
    A, B, C = gy[np.ix_(th, th)], gy[np.ix_(th, nu)], gy[np.ix_(nu, nu)]
    d = np.sqrt(np.diag(C))
    Cp = np.linalg.pinv(C / np.outer(d, d), rcond=rcond) / np.outer(d, d)
    g_th = A - B @ Cp @ B.T
    g_th = 0.5 * (g_th + g_th.T)
    return {"g_theta": g_th, "C": C, "pivot": pivot, "nu_index": nu,
            "cond_C_phipsi": float(np.linalg.cond((C / np.outer(d, d))[:2, :2]))}


def point(S, x, fac=1.0, model=D.APPROXIMANT, M_std=None, q_std=None):
    """Everything stored per point. fac scales FD_DELTA and K_STEPS (check (d))."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        r = metric_x(S, x, delta=D.FD_DELTA * fac, model=model, k_steps=D.K_STEPS * fac)
    pr = profile(r["g_x"], r["grad_iq0"])
    sign, logdet, cond = _scaled_logdet(pr["g_theta"])
    iq0 = r["iota_Q0"]
    log_pi = log_prior_int(x) + np.log(0.5 * np.sin(iq0))
    if M_std is None:
        M_std, q_std = D.window_std()
    Dth = np.array([M_std, q_std] + [D.SPIN_COMPONENT_STD] * 6 + [D.IOTA_STD])
    sgn_n, log_Nrho = np.linalg.slogdet(np.eye(9) + D.RHO ** 2 * Dth[:, None] * pr["g_theta"]
                                        * Dth[None, :])
    nu_names = [D.X_NAMES[i] for i in pr["nu_index"]]
    Dnu = np.array([D.NU_STD[k] for k in nu_names])
    ev = np.linalg.eigvalsh(D.RHO ** 2 * Dnu[:, None] * pr["C"] * Dnu[None, :])
    flags = list(r["flags"])
    if sign <= 0:
        flags.append("g_theta_not_positive")
    return {
        "x": np.asarray(x, float), "g_x": r["g_x"], "grad_iq0": r["grad_iq0"],
        "g_theta": pr["g_theta"], "logdet_g_theta": logdet if sign > 0 else np.nan,
        "cond_g_theta": cond, "log_pi_theta": log_pi,
        "log_s": 0.5 * logdet - log_pi if sign > 0 else np.nan,
        "log_N_rho": 0.5 * log_Nrho if sgn_n > 0 else np.nan,
        "n_nuisance": int(np.sum(ev > 1)), "nu_eig": ev, "pivot": pr["pivot"],
        "cond_C_phipsi": pr["cond_C_phipsi"], "iota_Q0": iq0, "chi_p": chi_p(x),
        "steps": r["steps"], "flags": flags,
    }


# ---- checks -------------------------------------------------------------------------------

def unit(S, h):
    return h / np.sqrt(S.inner(h, h))


def mismatch_tc(S, h1, h2, window=5e-3):
    """1 - max_{t_c} <h1^, h2^ e^{-2 pi i f t_c}> (no phase maximisation)."""
    from scipy.optimize import minimize_scalar
    a, b = unit(S, h1), unit(S, h2)
    fv = np.tile(S.f, len(D.DETECTORS))
    z = S.w * np.conj(a) * b

    def ov(t):
        return float(np.sum(z * np.exp(-2j * np.pi * fv * t)).real)

    grid = np.linspace(-window, window, 401)
    vals = [ov(t) for t in grid]
    i = int(np.argmax(vals))
    lo, hi = grid[max(i - 1, 0)], grid[min(i + 1, len(grid) - 1)]
    r = minimize_scalar(lambda t: -ov(t), bounds=(lo, hi), method="bounded",
                        options={"xatol": 1e-9})
    return 1 + r.fun, r.x


def schur(g, keep, drop):
    A, B, C = g[np.ix_(keep, keep)], g[np.ix_(keep, drop)], g[np.ix_(drop, drop)]
    return A - B @ np.linalg.pinv(C) @ B.T


class SplineCalibration:
    """bilby CubicSpline calibration factor (bilby/gw/detector/calibration.py, 2.6.0)."""

    def __init__(self, nodes_f, amp, phase):
        self.logf = np.log10(nodes_f)
        n = len(nodes_f)
        t1 = np.zeros((n, n))
        t1[0, :3] = [-1, 2, -1]
        t1[-1, -3:] = [-1, 2, -1]
        t2 = np.zeros((n, n))
        for i in range(1, n - 1):
            t1[i, i - 1:i + 2] = [1 / 6, 2 / 3, 1 / 6]
            t2[i, i - 1:i + 2] = [1, -2, 1]
        self.N = np.linalg.solve(t1, t2)
        self.amp, self.phase = np.asarray(amp), np.asarray(phase)

    def __call__(self, f):
        dl = self.logf[1] - self.logf[0]
        u = (np.log10(f) - self.logf[0]) / dl
        prev = np.clip(np.floor(u).astype(int), 0, len(self.logf) - 2)
        b = u - prev
        a = 1 - b
        c, d = (a ** 3 - a) / 6, (b ** 3 - b) / 6

        def ev(p):
            k = self.N @ p
            return a * p[prev] + b * p[prev + 1] + c * k[prev] + d * k[prev + 1]

        da, dp = ev(self.amp), ev(self.phase)
        return (1 + da) * (2 + 1j * dp) / (2 - 1j * dp)
