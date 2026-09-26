"""S1 checks (c) quadratic mismatch, (d) step convergence, (e) face-on aligned control,
(f) one-sided fraction, (g) cost. plan.md of t03, S1.

pixi run python tasks/t03-mismatch-volume/S1/controls.py --out tasks/t03-mismatch-volume/S1
"""
import argparse
import json
import time
import warnings
from multiprocessing import Pool

import numpy as np

from mismatch_metric import defaults as D
from mismatch_metric.batch import load_points
from mismatch_metric.metric import (Setup, _fd_plan, metric_x, mismatch_tc, point,
                                    polarizations, schur, signal, valid)

DATA = "data/t03-mismatch-volume"
TARGET = 1e-3
N_DIR = 5
S = None


def init():
    global S
    warnings.simplefilter("ignore")
    S = Setup()


def quad(args):
    """Check (c) at one point: 5 random directions in the first 10 coordinates. Direct mismatch
    at +dx and -dx (predicted 1e-3) and at +dx scaled to a predicted 1e-4."""
    label, x, seed = args
    rng = np.random.default_rng(seed)
    r = metric_x(S, x)
    keep, drop = list(range(10)), [D.I_TC]
    g = schur(r["g_x"], keep, drop)
    gu = schur(r["g_x_unproj"], keep, drop)
    h1 = r["h0"]

    def mm(dx):
        x2 = x.copy()
        x2[:10] += dx
        if not valid(x2):
            return np.nan
        return mismatch_tc(S, h1, signal(S, polarizations(S, x2[:10]), x[D.I_PSI], x[D.I_TC]))[0]

    out = []
    for _ in range(N_DIR):
        u = rng.normal(size=10) / np.sqrt(np.diag(g))
        dx = u * np.sqrt(2 * TARGET / (u @ g @ u))
        out.append({"plus": mm(dx), "minus": mm(-dx), "plus_1e-4": mm(dx * np.sqrt(0.1)),
                    "pred": 0.5 * dx @ g @ dx, "pred_unproj": 0.5 * dx @ gu @ dx})
    return label, out


def steps_conv(args):
    """Check (d): log det g^theta with steps h, h/2 (and 2h for the noise/truncation trend);
    h scales FD_DELTA and K_STEPS together."""
    label, x = args
    res = {}
    for name, fac in (("h", 1.0), ("h/2", 0.5), ("2h", 2.0)):
        r = point(S, x, fac=fac)
        res[name] = r["logdet_g_theta"]
    return label, res


def timed(args):
    label, x = args
    t0 = time.time()
    point(S, x)
    return time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", required=True)
    a = ap.parse_args()
    Xw, _ = load_points(DATA, "win")
    Xp, _ = load_points(DATA, "post")
    pts = [(f"post{i}", Xp[i]) for i in range(10)] + [(f"win{i}", Xw[i]) for i in range(10)]
    res = {"date": "2026-09-25", "fd_delta": D.FD_DELTA, "k_steps": D.K_STEPS.tolist(),
           "tapers_M": D.TAPERS_M, "target_mismatch": TARGET}
    with Pool(8, initializer=init) as pool:
        # (c)
        q = pool.map(quad, [(l, x, 100 + k) for k, (l, x) in enumerate(pts)])
        cases = [dict(c, point=l) for l, cs in q for c in cs]

        def frac(num, den):
            v = np.array([num(c) / den(c) - 1 for c in cases])
            v = v[np.isfinite(v)]
            return {"n": len(v), "frac_within_10pct": float(np.mean(np.abs(v) < 0.1)),
                    "p5_50_95": np.percentile(v, [5, 50, 95]).tolist()}

        one = lambda c: c["plus"] if np.isfinite(c["plus"]) else c["minus"]  # noqa: E731
        sym = lambda c: 0.5 * (c["plus"] + c["minus"])  # noqa: E731
        res["c"] = {
            "literal_1e-3": frac(one, lambda c: c["pred"]),
            "literal_1e-3_control_unprojected": frac(one, lambda c: c["pred_unproj"]),
            "symmetric_1e-3": frac(sym, lambda c: c["pred"]),
            "symmetric_1e-3_control_unprojected": frac(sym, lambda c: c["pred_unproj"]),
            "literal_1e-4": frac(lambda c: c["plus_1e-4"], lambda c: 0.1 * c["pred"]),
            "literal_1e-4_control_unprojected": frac(lambda c: c["plus_1e-4"],
                                                      lambda c: 0.1 * c["pred_unproj"]),
            "cases": cases}
        # (d)
        d = dict(pool.map(steps_conv, pts))
        diff = np.array([d[l]["h"] - d[l]["h/2"] for l, _ in pts])
        diff2 = np.array([d[l]["2h"] - d[l]["h"] for l, _ in pts])
        res["d"] = {"logdet": d, "max_abs_diff_h_vs_h2": float(np.nanmax(np.abs(diff))),
                    "n_within_0.05": int(np.sum(np.abs(diff) < 0.05)),
                    "max_abs_diff_2h_vs_h": float(np.nanmax(np.abs(diff2)))}
        # (g) cost: 40 window points
        tw = pool.map(timed, [(i, Xw[100 + i]) for i in range(40)])
        res["g"] = {"sec_per_point_mean": float(np.mean(tw)), "sec_per_point_max": float(np.max(tw))}
    init()
    # (e) face-on aligned
    xe = np.array([300.0, 0.8, 0, 0, 0.5, 0, 0, 0.5, 0.0, 0.3, 0.7, 0.0])
    try:
        r = point(S, xe)
        res["e"] = {"cond_C_phi_psi": r["cond_C_phipsi"], "log_s": r["log_s"],
                    "finite": bool(np.isfinite(r["log_s"])), "pivot": r["pivot"],
                    "iota_Q0_deg": float(np.degrees(r["iota_Q0"])), "flags": r["flags"]}
    except Exception as e:  # noqa: BLE001
        res["e"] = {"error": repr(e)}
    # (f) one-sided fraction, from the difference plan alone
    for name, X in (("win", Xw), ("post", Xp)):
        n1 = sum(any(_fd_plan(x, k, 2 * D.STEPS[k])[3] for k in range(10)) for x in X)
        res.setdefault("f", {})[f"{name}_frac_onesided"] = n1 / len(X)
    # (g) predicted total
    n_tot = len(Xw) + len(Xp)
    res["g"]["n_points"] = n_tot
    res["g"]["predicted_cpu_h"] = n_tot * res["g"]["sec_per_point_mean"] / 3600
    summ = {k: (v if k != "c" else {kk: vv for kk, vv in v.items() if kk != "cases"})
            for k, v in res.items()}
    print(json.dumps(summ, indent=1, default=float))
    with open(f"{a.out}/controls_{a.tag}.json", "w") as fh:
        json.dump(res, fh, indent=1, default=float)


if __name__ == "__main__":
    main()
