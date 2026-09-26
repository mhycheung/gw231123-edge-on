"""Controlled test (S3): does det g^theta follow the network signal norm when only psi changes?

pixi run python tasks/t03-mismatch-volume/S3/psi_scan.py
At 6 window points (the 3 with the largest s, all edge-on at merger, and 3 non-edge-on points
with s near the median), psi is set to 8 values in [0, pi/2) (the period of <h,h> in psi),
everything else fixed, and the S2 point calculation is repeated. Writes
tasks/t03-mismatch-volume/S3/psi_scan_<date>.json.
"""
import datetime
import glob
import json
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, "src")
from mismatch_metric.metric import Setup, point, polarizations, signal  # noqa: E402

_S = None


def _init():
    global _S
    _S = Setup()


def run(args):
    i, psi, x = args
    x = np.array(x)
    x[10] = psi
    r = point(_S, x)
    h = signal(_S, polarizations(_S, x[:10]), psi)
    return {"point": int(i), "psi": float(psi), "rho2_1000Mpc": _S.inner(h, h),
            "half_logdet": 0.5 * float(r["logdet_g_theta"]), "log_s": float(r["log_s"]),
            "iota_Q0_deg": float(np.degrees(r["iota_Q0"]))}


def main():
    fs = sorted(glob.glob("data/t03-mismatch-volume/chunks/win_0*.npz"))
    W = {k: np.concatenate([np.load(f)[k] for f in fs]) for k in ("point", "log_s", "iota_Q0", "x")}
    edge = np.abs(np.degrees(W["iota_Q0"]) - 90) < 20
    top = np.argsort(W["log_s"])[::-1][:3]
    ne = np.where(~edge)[0]
    med = ne[np.argsort(np.abs(W["log_s"][ne] - np.median(W["log_s"][ne])))[:3]]
    jobs = [(W["point"][j], p, W["x"][j].tolist()) for j in np.concatenate([top, med])
            for p in np.arange(8) * np.pi / 16]
    with Pool(8, initializer=_init) as pool:
        res = pool.map(run, jobs)
    date = datetime.date.today().isoformat()
    out = {"top_points": [int(W["point"][j]) for j in top],
           "median_non_edge_points": [int(W["point"][j]) for j in med],
           "stored_psi": {int(W["point"][j]): float(W["x"][j][10]) for j in np.concatenate([top, med])},
           "rows": res}
    fits = {}
    for i in out["top_points"] + out["median_non_edge_points"]:
        r = [row for row in res if row["point"] == i]
        lr = np.log([row["rho2_1000Mpc"] for row in r])
        ld = np.array([row["half_logdet"] for row in r])
        fits[i] = {"slope_half_logdet_vs_log_rho2": float(np.polyfit(lr, ld, 1)[0]),
                   "range_log_rho2": float(np.ptp(lr)), "range_half_logdet": float(np.ptp(ld))}
    out["fits"] = fits
    path = f"tasks/t03-mismatch-volume/S3/psi_scan_{date}.json"
    json.dump(out, open(path, "w"), indent=1)
    print(json.dumps(fits, indent=1))


if __name__ == "__main__":
    main()
