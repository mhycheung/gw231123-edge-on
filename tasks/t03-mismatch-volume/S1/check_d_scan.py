"""S1 check (d) diagnosis: log det g^theta against the waveform step scale FD_DELTA (K steps
fixed) and against the K step scale (FD_DELTA fixed), at the points where (d) failed."""
import json, warnings
import numpy as np
from multiprocessing import Pool
from mismatch_metric import defaults as D
from mismatch_metric.batch import load_points
from mismatch_metric.metric import Setup, metric_x, profile, _scaled_logdet
S = None
def init():
    global S; warnings.simplefilter("ignore"); S = Setup()
def ld(r):
    pr = profile(r["g_x"], r["grad_iq0"])
    return _scaled_logdet(pr["g_theta"])[1], np.linalg.eigvalsh(pr["g_theta"])[0]
def run(a):
    lab, x = a
    out = {"delta": {}, "kfac": {}}
    for dlt in (0.2, 0.1, 0.05, 0.025, 0.0125, 0.00625, 0.003125):
        v, e = ld(metric_x(S, x, delta=dlt)); out["delta"][dlt] = (round(v, 4), float(e))
    for kf in (4, 2, 1, 0.5, 0.25):
        v, e = ld(metric_x(S, x, k_steps=D.K_STEPS * kf)); out["kfac"][kf] = round(v, 4)
    return lab, out
Xw, _ = load_points("data/t03-mismatch-volume", "win"); Xp, _ = load_points("data/t03-mismatch-volume", "post")
pts = [("win2", Xw[2]), ("win5", Xw[5]), ("post0", Xp[0]), ("post1", Xp[1]), ("win0", Xw[0]), ("win7", Xw[7]), ("post3", Xp[3]), ("win1", Xw[1])]
with Pool(8, initializer=init) as p:
    res = dict(p.map(run, pts))
for k, v in res.items():
    print(k, "delta:", {d: a for d, (a, e) in v["delta"].items()}, "\n     lambda_min:", {d: f"{e:.2e}" for d, (a, e) in v["delta"].items()}, "\n     kfac:", v["kfac"])
json.dump({k: {kk: {str(a): b for a, b in vv.items()} for kk, vv in v.items()} for k, v in res.items()},
          open("tasks/t03-mismatch-volume/S1/check_d_scan_2026-09-25.json", "w"), indent=1)
