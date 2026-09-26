"""S1 debugging round 1: (i) the rebuilt FD waveform without taper equals LAL SimInspiralFD;
(ii) mismatch between the end-tapered and the PE waveform at the 20 check points;
(iii) jump scan along M, phi_ref, chi1z at post9 with and without the taper."""
import json, warnings
import numpy as np
from mismatch_metric import defaults as D
from mismatch_metric.batch import load_points
from mismatch_metric.metric import Setup, polarizations, signal, unit, mismatch_tc
warnings.simplefilter("ignore")
S = Setup()
Xw, _ = load_points("data/t03-mismatch-volume", "win")
Xp, _ = load_points("data/t03-mismatch-volume", "post")
pts = [Xp[i] for i in range(10)] + [Xw[i] for i in range(10)]
res = {"tapers_M": D.TAPERS_M}
rel, mm = [], []
for x in pts:
    a = polarizations(S, x[:10], lal_fd=True)
    b = polarizations(S, x[:10], tapers=None)
    rel.append(1 - S.inner(unit(S, signal(S, a, x[10])), unit(S, signal(S, b, x[10]))))
    ha = signal(S, a, x[10]); hc = signal(S, polarizations(S, x[:10]), x[10])
    mm.append(1 - S.inner(unit(S, ha), unit(S, hc)))
res["mismatch_untapered_vs_pe_max"] = float(max(rel))
res["mismatch_taper_vs_pe"] = {"max": float(max(mm)), "median": float(np.median(mm))}
x = Xp[9]
for k, span in ((0, 0.4), (9, 0.04), (4, 0.02)):
    vals = x[k] + np.linspace(-span / 2, span / 2, 401)
    for name, kw in (("pe", {"lal_fd": True}), ("taper", {})):
        H = []
        for v in vals:
            xx = x.copy(); xx[k] = v
            H.append(unit(S, signal(S, polarizations(S, xx[:10], **kw), x[10])))
        H = np.array(H)
        d2 = np.array([np.sqrt(S.inner(H[i + 2] - 2 * H[i + 1] + H[i], H[i + 2] - 2 * H[i + 1] + H[i])) for i in range(399)])
        d1 = np.array([np.sqrt(S.inner(H[i + 1] - H[i], H[i + 1] - H[i])) for i in range(400)])
        med = np.median(d2)
        res[f"scan_{D.X_NAMES[k]}_{name}"] = {"step": span / 400, "d1_median": float(np.median(d1)),
            "d2_median": float(med), "n_spikes_gt20med": int(np.sum(d2 > 20 * med)), "d2_max": float(d2.max())}
print(json.dumps(res, indent=1))
json.dump(res, open("tasks/t03-mismatch-volume/S1/check_taper_2026-09-25_round2.json", "w"), indent=1)
