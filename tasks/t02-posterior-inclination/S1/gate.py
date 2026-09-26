"""S1 gate of t02 (plan.md). Usage (repo root):
pixi run python tasks/t02-posterior-inclination/S1/gate.py <out.json>
Reads the test chunks in data/t02-posterior-inclination/test/.
"""
import datetime
import glob
import json
import subprocess
import sys
import warnings

import numpy as np

from merger_inclination.batch import T_E, read_samples, sample_params
from merger_inclination.frames import angle_between, unit_vector
from merger_inclination.inclination import emission_maxima, iota_Q
from merger_inclination.waveform import evaluate

warnings.simplefilter("ignore", UserWarning)
PE, LABEL = "data/t01-merger-inclination/posterior_samples.h5", "C00:NRSur7dq4"
T = "data/t02-posterior-inclination/test"
T01_IOTA_Q0_DEG = 88.71503841002698  # tasks/t01-merger-inclination/S3/peak_candidates_2026-09-25.json

C = {s: [np.load(f) for f in sorted(glob.glob(f"{T}/{s}_*.npz"))] for s in ("post", "prior")}
out = {"date": datetime.date.today().isoformat(), "script": "tasks/t02-posterior-inclination/S1/gate.py",
       "src_commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()}

# (a) ML sample reproduces t01, and the must-fail control
ml = [c for c in C["post"] if c["index"][0] == 6096][0]
a_val = float(np.degrees(ml["iota_Q0"][0]))
S = read_samples(PE, LABEL, "post")
p = sample_params(S, 6096)
wf = evaluate(p)
N_wrong = unit_vector(p["iota"], p["phase"])
ctrl = float(np.degrees(iota_Q(wf, N_wrong, 0.0)))
out["a"] = {"iota_Q0_deg": a_val, "t01": T01_IOTA_Q0_DEG, "diff_deg": a_val - T01_IOTA_Q0_DEG,
            "control_wrong_N_deg": ctrl, "pass": abs(a_val - T01_IOTA_Q0_DEG) < 1e-6,
            "control_fails_as_required": abs(ctrl - T01_IOTA_Q0_DEG) > 1.0}

# (b), (c), (e)
for s in ("post", "prior"):
    ok = np.concatenate([~c["failed"] for c in C[s]])
    d = np.concatenate([np.abs(c["iota_Q_tref"] - c["iota_input"]) for c in C[s]])[ok]
    sec = np.concatenate([c["seconds"] for c in C[s]])
    out[s] = {"n": int(ok.size), "failed": int((~ok).sum()),
              "errors": sorted({e.strip().splitlines()[-1] for c in C[s] for e in c["errors"] if e})[:5],
              "max_abs_iotaQ_tref_minus_iota_rad": float(d.max()), "b_pass": bool(d.max() < 1e-3),
              "sec_per_sample_mean": float(sec.mean()), "sec_per_sample_p95": float(np.percentile(sec, 95)),
              "helicity_E_positive_frac": float(np.mean(np.concatenate([c["helicity_E"] for c in C[s]])[ok] > 0)),
              "helicity_ambiguous0": int(np.concatenate([c["helicity_ambiguous0"] for c in C[s]]).sum())}
out["c_pass"] = all(out[s]["failed"] / out[s]["n"] < 0.01 for s in ("post", "prior"))

# (d) tracked iota_E vs fresh full-sphere search at t = -100 M and -1000 M
rng = np.random.default_rng(0)
picks = [("post", 6096)] + [(s, int(i)) for s, i in zip(rng.choice(["post", "prior"], 20), rng.integers(0, 100, 20))]
rows = []
for s, i in picks:
    c = [c for c in C[s] if i in c["index"]][0]
    j = int(np.where(c["index"] == i)[0][0])
    if c["failed"][j]:
        continue
    wf = evaluate(sample_params(read_samples(PE, LABEL, s) if s == "prior" else S, i))
    for t in (-100.0, -1000.0):
        k = int(np.where(T_E == t)[0][0])
        fresh = emission_maxima(wf, t)["e"]
        rows.append({"set": s, "index": i, "t": t,
                     "angle_deg": float(np.degrees(angle_between(c["e_E"][j, k], fresh)))})
ang = np.array([r["angle_deg"] for r in rows])
out["d"] = {"n": len(rows), "frac_within_0.1deg": float(np.mean(ang < 0.1)),
            "worst": sorted(rows, key=lambda r: -r["angle_deg"])[:5], "pass": bool(np.mean(ang < 0.1) >= 0.95)}

sec = np.mean([out["post"]["sec_per_sample_mean"], out["prior"]["sec_per_sample_mean"]])
out["e"] = {"sec_per_sample": float(sec), "cpu_h_total": float(sec * (18185 + 5000) / 3600),
            "chunk_size_for_15min": int(900 // sec)}
out["gate_pass"] = bool(out["a"]["pass"] and out["a"]["control_fails_as_required"] and out["post"]["b_pass"]
                        and out["prior"]["b_pass"] and out["c_pass"] and out["d"]["pass"])
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out, indent=1))
