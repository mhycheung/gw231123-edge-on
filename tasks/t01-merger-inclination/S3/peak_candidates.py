"""Local maxima of |h(t, N)| within 15% of the global one, with iota_Q and iota_E at each.

Usage (repo root): pixi run python tasks/t01-merger-inclination/S3/peak_candidates.py <out.json>
Also: max of iota_Q(t) over t < 20 M (v2 frame freeze after that), and iota_Q at t = 0.
"""
import datetime, json, subprocess, sys

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.signal import argrelmax

from merger_inclination.frames import angle_between, angles, line_of_sight
from merger_inclination.inclination import emission_maxima, iota_Q
from merger_inclination.params import read_pe_sample
from merger_inclination.waveform import evaluate

p = read_pe_sample("data/t01-merger-inclination/posterior_samples.h5", "C00:NRSur7dq4")
N = line_of_sight(p["iota"], p["phase"])
th, ph = angles(N)
out = {"script": "tasks/t01-merger-inclination/S3/peak_candidates.py",
       "src_commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
       "date": datetime.date.today().isoformat(), "input_index": p["index"], "models": {}}
for model in ["NRSur7dq4v2", "NRSur7dq4"]:
    wf = evaluate(p, model=model)
    Y = wf.ylm_matrix(th, ph)[0]
    a = np.abs(wf.H @ Y)
    rows = []
    for i in argrelmax(a)[0]:
        if a[i] < 0.85 * a.max():
            continue
        r = minimize_scalar(lambda t: -abs(wf.modes_at(t) @ Y), bounds=(wf.t[i-1], wf.t[i+1]),
                            method="bounded", options={"xatol": 0.01})
        em = emission_maxima(wf, r.x)
        rows.append({"t_M": float(r.x), "abs_h_rel_to_max": float(-r.fun / a.max()),
                     "iota_Q_deg": float(np.degrees(iota_Q(wf, N, r.x))),
                     "iota_E_deg": float(np.degrees(angle_between(em["e"], N)))})
    m = wf.t < 20
    iq = np.degrees(iota_Q(wf, N, wf.t[m]))
    out["models"][model] = {"peaks": rows, "iota_Q_max_deg_t_lt_20M": float(iq.max()),
                            "t_of_iota_Q_max_M": float(wf.t[m][iq.argmax()]),
                            "iota_Q_at_t0_deg": float(np.degrees(iota_Q(wf, N, 0.0))),
                            "iota_Q_at_t_minus_1000M_deg": float(np.degrees(iota_Q(wf, N, -1000.0))),
                            "iota_Q_min_deg_t_gt_minus_1000M": float(np.degrees(iota_Q(wf, N, wf.t[(wf.t > -1000) & m])).min())}
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out["models"], indent=1))
