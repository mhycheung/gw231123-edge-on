"""S1 debugging: check (c) along the same directions at predicted mismatches 1e-3, 1e-4, 1e-5.
Relative error from cubic terms scales as sqrt(target); error in the metric does not."""
import json, warnings
import numpy as np
from multiprocessing import Pool
from mismatch_metric import defaults as D
from mismatch_metric.batch import load_points
from mismatch_metric.metric import Setup, metric_x, mismatch_tc, polarizations, schur, signal, valid
S = None
def init():
    global S; warnings.simplefilter("ignore"); S = Setup()
def run(args):
    label, x, seed = args
    rng = np.random.default_rng(seed)
    r = metric_x(S, x)
    g = schur(r["g_x"], list(range(10)), [D.I_TC])
    out = []
    for _ in range(5):
        u = rng.normal(size=10) / np.sqrt(np.diag(g))
        row = {}
        for T in (1e-3, 1e-4, 1e-5):
            dx = u * np.sqrt(2 * T / (u @ g @ u))
            x2 = x.copy(); x2[:10] += dx
            if not valid(x2):
                x2[:10] -= 2 * dx
                if not valid(x2): break
            mm, _ = mismatch_tc(S, r["h0"], signal(S, polarizations(S, x2[:10]), x[10]))
            row[T] = mm / T - 1
        # antisymmetric part: mismatch at +dx and -dx at T=1e-3 (cubic terms flip sign)
        dx = u * np.sqrt(2e-3 / (u @ g @ u))
        xp, xm = x.copy(), x.copy(); xp[:10] += dx; xm[:10] -= dx
        if valid(xp) and valid(xm):
            mp, _ = mismatch_tc(S, r["h0"], signal(S, polarizations(S, xp[:10]), x[10]))
            mn, _ = mismatch_tc(S, r["h0"], signal(S, polarizations(S, xm[:10]), x[10]))
            row["sym_1e-3"] = (mp + mn) / 2e-3 - 1
        out.append(row)
    return label, out
Xw, _ = load_points("data/t03-mismatch-volume", "win"); Xp, _ = load_points("data/t03-mismatch-volume", "post")
pts = [(f"post{i}", Xp[i]) for i in range(10)] + [(f"win{i}", Xw[i]) for i in range(10)]
with Pool(8, initializer=init) as p:
    res = dict(p.map(run, [(l, x, 100 + k) for k, (l, x) in enumerate(pts)]))
summ = {}
for key in (1e-3, 1e-4, 1e-5, "sym_1e-3"):
    v = np.array([r[key] for rs in res.values() for r in rs if key in r])
    summ[str(key)] = {"n": len(v), "frac_within_10pct": float(np.mean(np.abs(v) < 0.1)),
                      "p5_50_95": np.percentile(v, [5, 50, 95]).round(4).tolist(),
                      "median_abs": float(np.median(np.abs(v)))}
print(json.dumps(summ, indent=1))
json.dump({"summary": summ, "cases": {k: [{str(a): b for a, b in r.items()} for r in v] for k, v in res.items()}},
          open("tasks/t03-mismatch-volume/S1/check_c_scaling_2026-09-25.json", "w"), indent=1)
