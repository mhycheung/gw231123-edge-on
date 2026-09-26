"""Peak time t*, iota_Q (coprecessing axis) and iota_E (direction of maximum emission)."""

import numpy as np
from scipy.optimize import minimize, minimize_scalar

from .defaults import DEFAULTS
from .frames import (angle_between, angles, fibonacci_sphere, line_of_sight,
                     quat_rotate_z, tangent_basis)
from .waveform import evaluate


def peak_time(wf, theta, phi, tol=DEFAULTS["peak_tol"]):
    """t* = argmax_t |h(t, n)|, refined on the mode splines to `tol` (M)."""
    a = np.abs(wf.strain(theta, phi))
    i = int(np.argmax(a))
    if i in (0, len(a) - 1):
        raise RuntimeError("peak of |h| at the edge of the time grid")
    Y = wf.ylm_matrix(theta, phi)[0]
    dt = wf.t[1] - wf.t[0]
    r = minimize_scalar(lambda t: -abs(wf.modes_at(t) @ Y),
                        bounds=(wf.t[i] - dt, wf.t[i] + dt), method="bounded",
                        options={"xatol": tol})
    return float(r.x)


def z_copr(wf, t):
    """Coprecessing-frame z axis in the inertial (source) frame at time(s) t."""
    return quat_rotate_z(wf.quat_at(t))


def iota_Q(wf, N, t):
    return angle_between(z_copr(wf, t), N)


def _F(wf, hvec, n):
    th, ph = angles(n)
    return np.abs(wf.ylm_matrix(th, ph) @ hvec)


def _refine(wf, hvec, n0, tol, step=0.02):
    """Local maximum of |h(n)| near n0, Nelder-Mead in the tangent plane of n0."""
    u, v = tangent_basis(n0)

    def vec(x):
        n = n0 + x[0] * u + x[1] * v
        return n / np.linalg.norm(n)

    r = minimize(lambda x: -_F(wf, hvec, vec(x)[None])[0], np.zeros(2), method="Nelder-Mead",
                 options={"xatol": tol, "fatol": 1e-14,
                          "initial_simplex": [[0, 0], [step, 0], [0, step]],
                          "maxiter": 2000})
    return vec(r.x), -r.fun


def helicity(wf, n, t):
    """d arg h(t, n) / dt at time t (rad/M). Negative along +L in the LAL convention."""
    th, ph = angles(np.asarray(n)[None])
    Y = wf.ylm_matrix(th, ph)[0]
    h, hd = wf.modes_at(t) @ Y, wf.modes_at(t, 1) @ Y
    return float(np.imag(hd / h))


def emission_maxima(wf, t, n_sphere=DEFAULTS["n_sphere"], tol=DEFAULTS["angle_tol"]):
    """The two maxima of |h(t, n)| over the sphere, oriented by helicity.

    Returns dict: e (maximum with negative helicity), e_opp (the other), their |h| and
    helicities, and 'helicity_ambiguous' if both have the same sign.
    """
    hvec = wf.modes_at(t)
    G = fibonacci_sphere(n_sphere)
    Fg = _F(wf, hvec, G)
    n1, F1 = _refine(wf, hvec, G[np.argmax(Fg)], tol)
    opp = G @ n1 < 0
    n2, F2 = _refine(wf, hvec, G[opp][np.argmax(Fg[opp])], tol)
    w1, w2 = helicity(wf, n1, t), helicity(wf, n2, t)
    ambiguous = (w1 < 0) == (w2 < 0)
    if w1 < 0 or (ambiguous and F1 >= F2):
        e, e_opp, Fe, Fo, we, wo = n1, n2, F1, F2, w1, w2
    else:
        e, e_opp, Fe, Fo, we, wo = n2, n1, F2, F1, w2, w1
    return {"e": e, "e_opp": e_opp, "F_e": Fe, "F_opp": Fo, "helicity_e": we,
            "helicity_opp": wo, "helicity_ambiguous": bool(ambiguous),
            "F_grid_max": float(Fg.max())}


def track_emission(wf, e0, t0, times, tol=1e-5):
    """e(t) on `times`, each maximised from the previous time's axis, starting at (t0, e0)."""
    times = np.asarray(times)
    out = np.zeros((len(times), 3))
    k0 = int(np.argmin(np.abs(times - t0)))
    for order in (range(k0, len(times)), range(k0 - 1, -1, -1)):
        n = np.asarray(e0)
        for k in order:
            n, _ = _refine(wf, wf.modes_at(times[k]), n, tol, step=0.01)
            out[k] = n
    return out


def compute(p, model=DEFAULTS["model"], dt=DEFAULTS["dt"], f_low=DEFAULTS["f_low"],
            series=True):
    """Full calculation for parameter dict p. Returns (result dict, waveform)."""
    wf = evaluate(p, model=model, dt=dt, f_low=f_low)
    N = line_of_sight(p["iota"], p["phase"])
    thN, phN = angles(N)
    ts = peak_time(wf, thN, phN)
    zq = z_copr(wf, ts)
    em = emission_maxima(wf, ts)
    A_tot = np.sqrt(np.sum(np.abs(wf.H) ** 2, axis=1))
    res = {
        "model": model,
        "t_star_M": ts,
        "t_ref_M": wf.t_ref,
        "t_peak_total_amp_grid_M": float(wf.t[np.argmax(A_tot)]),
        "f_ref_geom": wf.f_ref_geom,
        "N": N.tolist(),
        "iota_Q": float(angle_between(zq, N)),
        "iota_E": float(angle_between(em["e"], N)),
        "z_copr_t_star": zq.tolist(),
        "e": em["e"].tolist(),
        "e_opp": em["e_opp"].tolist(),
        "angle_e_opp_from_minus_e": float(angle_between(em["e_opp"], -em["e"])),
        "F_opp_over_F_e": float(em["F_opp"] / em["F_e"]),
        "angle_e_zcopr": float(angle_between(em["e"], zq)),
        "helicity_e": em["helicity_e"],
        "helicity_opp": em["helicity_opp"],
        "helicity_ambiguous": em["helicity_ambiguous"],
        "iota_Q_at_t_ref": float(iota_Q(wf, N, wf.t_ref)),
        "iota_input": p["iota"],
        "t_star_after_frame_freeze": bool(ts > 0),
    }
    if series:
        res["_series"] = {
            "t_Q": wf.t, "iota_Q": iota_Q(wf, N, wf.t),
        }
        tE = np.arange(ts - DEFAULTS["series_before"], ts + DEFAULTS["series_after"] + 1e-9,
                       DEFAULTS["series_step"])
        tE = tE[(tE >= wf.t[0]) & (tE <= wf.t[-1])]
        eE = track_emission(wf, em["e"], ts, tE)
        res["_series"].update({"t_E": tE, "e_E": eE, "iota_E": angle_between(eE, N)})
    return res, wf
