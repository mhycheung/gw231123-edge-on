"""Network <h,h> at 1000 Mpc for every S2 point: the diagnostic of the heavy tail of s (S3).

pixi run python tasks/t03-mismatch-volume/S3/signal_norm.py [--n N] [--procs P]
Writes data/t03-mismatch-volume/signal_norm_<date>.npz: for sets W and P, per point, the
network <h,h> at the point's psi (rho2), and its mean and maximum over psi (rho2_mean,
rho2_max). <s,s> as a function of psi is a + b cos 4psi + c sin 4psi; three psi values fix it.
Same waveform (tapers) and inner product as the metric (src/mismatch_metric/metric.py).
"""
import argparse
import datetime
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, "src")
from mismatch_metric import defaults as D  # noqa: E402
from mismatch_metric.metric import Setup, polarizations, signal  # noqa: E402

OUT = "data/t03-mismatch-volume"
_S = None


def _init():
    global _S
    _S = Setup()


def norms(x):
    pols = polarizations(_S, x[:10])
    v = [_S.inner(s, s) for s in (signal(_S, pols, p) for p in (0.0, np.pi / 8, np.pi / 4))]
    a = 0.5 * (v[0] + v[2])                 # v(0) = a + b, v(pi/8) = a + c, v(pi/4) = a - b
    b, c = v[0] - a, v[1] - a
    psi = x[10]
    return (a + b * np.cos(4 * psi) + c * np.sin(4 * psi), a, a + np.hypot(b, c))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--procs", type=int, default=os.cpu_count())
    a = ap.parse_args()
    out = {}
    with Pool(a.procs, initializer=_init) as pool:
        for s in ("win", "post"):
            x = np.load(f"{OUT}/{s}_points.npz")["x"][: a.n]
            r = np.array(pool.map(norms, list(x), chunksize=20))
            out[f"{s}_rho2"], out[f"{s}_rho2_mean"], out[f"{s}_rho2_max"] = r.T
    date = datetime.date.today().isoformat()
    tag = "" if a.n is None else f"_n{a.n}"
    np.savez(f"{OUT}/signal_norm_{date}{tag}.npz", **out)
    print("wrote", f"{OUT}/signal_norm_{date}{tag}.npz")


if __name__ == "__main__":
    main()
