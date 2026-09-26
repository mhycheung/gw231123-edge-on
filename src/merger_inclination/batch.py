"""Inclination vs time for many samples (posterior or prior), in chunks.

pixi run python -m merger_inclination.batch --pe FILE --label LABEL --set post|prior \
    --start i0 --stop i1 --out DIR
Writes DIR/<set>_<i0:05d>_<i1:05d>.npz; skips the chunk if that file exists.
"""

import argparse
import os
import time
import traceback
import warnings

import h5py
import numpy as np

from .frames import angle_between, line_of_sight
from .inclination import emission_maxima, helicity, iota_Q, track_emission
from .params import FIELDS, _scalar
from .waveform import evaluate

# Time grids (M), plan.md of t02
T_Q = np.arange(-4300.0, 100.0 + 0.5, 1.0)
T_E = np.concatenate([np.arange(-1000.0, -200.0 + 1e-9, 20.0), np.arange(-195.0, 50.0 + 1e-9, 5.0)])
assert len(T_E) == 91 and 0.0 in T_E


def read_samples(path, label, which):
    """Dict of parameter arrays for the posterior ('post') or the stored prior ('prior')."""
    with h5py.File(path, "r") as f:
        g = f[label]
        f_ref = float(_scalar(g["meta_data/meta_data/f_ref"]))
        if which == "post":
            ps = g["posterior_samples"][()]
            out = {k: np.asarray(ps[k], float) for k in FIELDS}
        elif which == "prior":
            ps = g["priors/samples"]
            out = {k: np.asarray(ps[k][()], float) for k in FIELDS}
        else:
            raise ValueError(which)
    out["f_ref"] = f_ref
    return out


def sample_params(S, i):
    p = {k: float(S[k][i]) for k in FIELDS}
    p["f_ref"] = S["f_ref"]
    return p


def sample_inclination(p, model="NRSur7dq4v2"):
    """iota_Q on T_Q, iota_E on T_E (tracked from t = 0), and scalars, for one sample."""
    wf = evaluate(p, model=model)
    N = line_of_sight(p["iota"], p["phase"])
    tq = T_Q[(T_Q >= wf.t[0]) & (T_Q <= wf.t[-1])]
    iq = np.full(T_Q.shape, np.nan)
    iq[np.isin(T_Q, tq)] = iota_Q(wf, N, tq)
    em = emission_maxima(wf, 0.0)
    eE = track_emission(wf, em["e"], 0.0, T_E)
    hel = np.array([helicity(wf, n, t) for n, t in zip(eE, T_E)])
    return {
        "iota_Q": iq, "iota_E": angle_between(eE, N), "e_E": eE, "helicity_E": hel,
        "iota_Q0": float(iota_Q(wf, N, 0.0)), "iota_E0": float(angle_between(em["e"], N)),
        "t_ref": wf.t_ref, "iota_Q_tref": float(iota_Q(wf, N, wf.t_ref)),
        "helicity_ambiguous0": em["helicity_ambiguous"],
    }


def run_chunk(pe, label, which, start, stop, out_dir, model="NRSur7dq4v2"):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{which}_{start:05d}_{stop:05d}.npz")
    if os.path.exists(path):
        print("exists, skipping:", path)
        return path
    S = read_samples(pe, label, which)
    stop = min(stop, len(S["iota"]))
    idx = np.arange(start, stop)
    n = len(idx)
    R = {"iota_Q": np.full((n, len(T_Q)), np.nan, np.float32),
         "iota_E": np.full((n, len(T_E)), np.nan, np.float32),
         "e_E": np.full((n, len(T_E), 3), np.nan, np.float32),
         "helicity_E": np.full((n, len(T_E)), np.nan, np.float32)}
    for k in ("iota_Q0", "iota_E0", "t_ref", "iota_Q_tref", "seconds"):
        R[k] = np.full(n, np.nan)
    R["helicity_ambiguous0"] = np.zeros(n, bool)
    R["failed"] = np.zeros(n, bool)
    errors = [""] * n
    for j, i in enumerate(idx):
        t0 = time.time()
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                r = sample_inclination(sample_params(S, i), model=model)
            for k, v in r.items():
                R[k][j] = v
        except Exception:  # record and continue; failures are counted in S2/S3
            R["failed"][j] = True
            errors[j] = traceback.format_exc(limit=2)[-500:]
        R["seconds"][j] = time.time() - t0
    np.savez(path + ".tmp.npz", index=idx, T_Q=T_Q, T_E=T_E, errors=np.array(errors),
             iota_input=S["iota"][idx], M=S["mass_1"][idx] + S["mass_2"][idx],
             q=S["mass_1"][idx] / S["mass_2"][idx], model=model, **R)
    os.replace(path + ".tmp.npz", path)  # atomic: a chunk file exists only when complete
    print(f"wrote {path}: {n} samples, {R['failed'].sum()} failed, "
          f"{np.nanmean(R['seconds']):.2f} s/sample")
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pe", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--set", choices=["post", "prior"], required=True)
    ap.add_argument("--start", type=int, required=True)
    ap.add_argument("--stop", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="NRSur7dq4v2")
    a = ap.parse_args(argv)
    run_chunk(a.pe, a.label, a.set, a.start, a.stop, a.out, a.model)


if __name__ == "__main__":
    main()
