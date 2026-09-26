"""S1 check (a): optimal SNR of the ML sample from our waveform vs the stored values."""
import h5py, json, numpy as np
from mismatch_metric import defaults as D
from mismatch_metric.metric import Setup, polarizations, signal, SplineCalibration

D.check_pe_constants()
S = Setup()
with h5py.File(D.PE_FILE) as f:
    ps = f[D.LABEL]["posterior_samples"][()]
p = ps[D.ML_INDEX]
x = [p["mass_1"] + p["mass_2"], p["mass_2"] / p["mass_1"], p["spin_1x"], p["spin_1y"],
     p["spin_1z"], p["spin_2x"], p["spin_2y"], p["spin_2z"], p["iota"], p["phase"]]
pols = polarizations(S, x, distance=p["luminosity_distance"])
cal = {d: SplineCalibration([p[f"recalib_{d}_frequency_{i}"] for i in range(10)],
                            [p[f"recalib_{d}_amplitude_{i}"] for i in range(10)],
                            [p[f"recalib_{d}_phase_{i}"] for i in range(10)]) for d in D.DETECTORS}
n = len(S.f)
out = {}
for c_name, c in (("no_calibration", None), ("with_calibration", cal)):
    s = signal(S, pols, p["psi"], 0.0, calibration=c)
    for k, d in enumerate(D.DETECTORS):
        seg = slice(k * n, (k + 1) * n)
        snr = np.sqrt(np.sum(S.w[seg] * np.abs(s[seg]) ** 2))
        out[f"{d}_{c_name}"] = snr
        out[f"{d}_{c_name}_rel_diff"] = snr / p[f"{d}_optimal_snr"] - 1
for d in D.DETECTORS:
    out[f"{d}_stored"] = float(p[f"{d}_optimal_snr"])
print(json.dumps({k: float(v) for k, v in out.items()}, indent=1))
