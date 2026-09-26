"""Point sets and the chunk runner.

pixi run python -m mismatch_metric.batch --make-points --out DIR
pixi run python -m mismatch_metric.batch --set win|post --chunk k --size n --out DIR [--fac f]
Writes DIR/chunks/<set>_<k:04d>.npz (<set>_fac<f>_<k:04d>.npz if f != 1: steps scaled by f,
the step check of S2); skips the chunk if that file exists.
Point files: DIR/win_points.npz, DIR/post_points.npz (made once, seed D.SEED).
"""

import argparse
import os
import subprocess
import time
import traceback
import warnings

import h5py
import numpy as np

from . import defaults as D
from .metric import Setup, point


def make_win_points(n=D.N_WIN, seed=D.SEED):
    """Draws from the PE prior restricted to the (M, q) window; t_c = 0.

    (M, q): density M / (1 + q)^2 on the rectangle (uniform in m1, m2), by rejection.
    Spins: a ~ U(0, A_MAX), isotropic. iota: cos uniform; phi_ref ~ U(0, 2 pi); psi ~ U(0, pi).
    """
    rng = np.random.default_rng(seed)
    wmax = D.M_WINDOW[1] / (1 + D.Q_WINDOW[0]) ** 2
    M, q = [], []
    while len(M) < n:
        m = rng.uniform(*D.M_WINDOW, 4 * n)
        qq = rng.uniform(*D.Q_WINDOW, 4 * n)
        keep = rng.uniform(0, wmax, 4 * n) < m / (1 + qq) ** 2
        M.extend(m[keep])
        q.extend(qq[keep])
    M, q = np.array(M[:n]), np.array(q[:n])

    def spins():
        a = rng.uniform(0, D.A_MAX, n)
        v = rng.normal(size=(n, 3))
        return a[:, None] * v / np.linalg.norm(v, axis=1)[:, None]

    c1, c2 = spins(), spins()
    iota = np.arccos(rng.uniform(-1, 1, n))
    phi = rng.uniform(0, 2 * np.pi, n)
    psi = rng.uniform(0, np.pi, n)
    x = np.column_stack([M, q, c1, c2, iota, phi, psi, np.zeros(n)])
    return x, np.arange(n)


def make_post_points(n=D.N_POST, seed=D.SEED, pe=D.PE_FILE):
    """n random posterior samples (seed) plus the ML sample, as x; t_c = 0."""
    with h5py.File(pe, "r") as f:
        ps = f[D.LABEL]["posterior_samples"][()]
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(ps), n, replace=False)
    idx = np.append(idx, D.ML_INDEX)
    p = ps[idx]
    x = np.column_stack([p["mass_1"] + p["mass_2"], p["mass_2"] / p["mass_1"],
                         p["spin_1x"], p["spin_1y"], p["spin_1z"],
                         p["spin_2x"], p["spin_2y"], p["spin_2z"],
                         p["iota"], p["phase"], p["psi"], np.zeros(len(idx))])
    return x, idx


def load_points(out, which):
    z = np.load(os.path.join(out, f"{which}_points.npz"))
    return z["x"], z["index"]


def run_chunk(which, k, size, out, v2=None, fac=1.0):
    """Evaluate points [k*size, (k+1)*size) of set `which`; iota_Q(0) also with v2 for 'post'."""
    cdir = os.path.join(out, "chunks")
    os.makedirs(cdir, exist_ok=True)
    tag = which if fac == 1.0 else f"{which}_fac{fac:g}"
    path = os.path.join(cdir, f"{tag}_{k:04d}.npz")
    if os.path.exists(path):
        print("exists, skipping:", path)
        return path
    X, index = load_points(out, which)
    sel = np.arange(k * size, min((k + 1) * size, len(X)))
    n = len(sel)
    v2 = (which == "post") if v2 is None else v2
    S = Setup()
    M_std, q_std = D.window_std()
    R = {"g_x": np.full((n, 12, 12), np.nan), "grad_iq0": np.full((n, 12), np.nan),
         "g_theta": np.full((n, 9, 9), np.nan), "nu_eig": np.full((n, 3), np.nan),
         "steps": np.full((n, 10), np.nan)}
    for key in ("logdet_g_theta", "cond_g_theta", "log_pi_theta", "log_s", "log_N_rho",
                "iota_Q0", "chi_p", "cond_C_phipsi", "seconds", "iota_Q0_v2"):
        R[key] = np.full(n, np.nan)
    R["n_nuisance"] = np.full(n, -1)
    R["pivot"] = np.full(n, -1)
    R["failed"] = np.zeros(n, bool)
    flags, errors = [""] * n, [""] * n
    for j, i in enumerate(sel):
        t0 = time.time()
        try:
            r = point(S, X[i], fac=fac, M_std=M_std, q_std=q_std)
            for key in R:
                if key in r:
                    R[key][j] = r[key]
            flags[j] = ";".join(r["flags"])
            if v2:
                from merger_inclination.frames import line_of_sight
                from merger_inclination.inclination import iota_Q
                from merger_inclination.waveform import evaluate
                from .metric import _pdict
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    wf = evaluate(_pdict(X[i]), model="NRSur7dq4v2", dt=D.SUR_DT)
                R["iota_Q0_v2"][j] = iota_Q(wf, line_of_sight(X[i][8], X[i][9]), 0.0)
        except Exception:  # record and continue; failures are counted in S2/S3
            R["failed"][j] = True
            errors[j] = traceback.format_exc(limit=3)[-800:]
        R["seconds"][j] = time.time() - t0
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                            text=True).stdout.strip()
    np.savez(path + ".tmp.npz", point=sel, index=index[sel], x=X[sel], flags=np.array(flags),
             errors=np.array(errors), fd_delta=D.FD_DELTA * fac, k_steps=D.K_STEPS * fac,
             tapers_M=D.TAPERS_M, src_commit=commit, **R)
    os.replace(path + ".tmp.npz", path)  # atomic: a chunk file exists only when complete
    print(f"wrote {path}: {n} points, {R['failed'].sum()} failed, "
          f"{np.nanmean(R['seconds']):.2f} s/point")
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--make-points", action="store_true")
    ap.add_argument("--set", choices=["win", "post"])
    ap.add_argument("--chunk", type=int)
    ap.add_argument("--size", type=int)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fac", type=float, default=1.0)
    a = ap.parse_args(argv)
    if a.make_points:
        os.makedirs(a.out, exist_ok=True)
        for which, fn in (("win", make_win_points), ("post", make_post_points)):
            path = os.path.join(a.out, f"{which}_points.npz")
            if os.path.exists(path):
                print("exists, not overwritten:", path)
                continue
            x, idx = fn()
            np.savez(path, x=x, index=idx, seed=D.SEED, x_names=np.array(D.X_NAMES))
            print("wrote", path, x.shape)
        return
    run_chunk(a.set, a.chunk, a.size, a.out, fac=a.fac)


if __name__ == "__main__":
    main()
