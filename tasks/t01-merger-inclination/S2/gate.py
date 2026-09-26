"""S2 convention gate (plan.md of t01): our mode sum at N vs LALSimulation NRSur7dq4.

Usage (repo root): pixi run python tasks/t01-merger-inclination/S2/gate.py <out.json>
Pass: relative L2 difference of h = h+ - i hx over [t* - 500 M, t* + 50 M] < 1e-2 (after
aligning peak times); the two wrong-convention controls must give > 1e-1.
"""

import datetime
import json
import subprocess
import sys

import lal
import lalsimulation as ls
import numpy as np
from scipy.interpolate import CubicSpline

from merger_inclination.frames import angles, line_of_sight, unit_vector
from merger_inclination.inclination import peak_time
from merger_inclination.params import read_pe_sample
from merger_inclination.waveform import MTSUN_SI, evaluate, load_surrogate

PE = "data/t01-merger-inclination/posterior_samples.h5"
LABEL = "C00:NRSur7dq4"
FS = 4096.0  # LAL sampling rate, Hz
WIN = (-500.0, 50.0)  # window around t*, M
PASS, FAIL = 1e-2, 1e-1

p = read_pe_sample(PE, LABEL)
assert p["approximant"] == "NRSur7dq4", p["approximant"]
M = p["mass_1"] + p["mass_2"]
tM = M * MTSUN_SI                 # seconds per M
D = p["luminosity_distance"] * 1e6 * lal.PC_SI

hp, hc = ls.SimInspiralChooseTDWaveform(
    p["mass_1"] * lal.MSUN_SI, p["mass_2"] * lal.MSUN_SI,
    p["spin_1x"], p["spin_1y"], p["spin_1z"], p["spin_2x"], p["spin_2y"], p["spin_2z"],
    D, p["iota"], p["phase"], 0.0, 0.0, 0.0, 1 / FS, 0.0, p["f_ref"], lal.CreateDict(),
    ls.GetApproximantFromString("NRSur7dq4"))
tL = (float(hp.epoch) + np.arange(hp.data.length) / FS) / tM          # M
hL = (hp.data.data - 1j * hc.data.data) * D / (M * lal.MRSUN_SI)       # geometric, M/r

wf = evaluate(p, model="NRSur7dq4", dt=0.1, f_low=0.0)
N = line_of_sight(p["iota"], p["phase"])
thN, phN = angles(N)
t_star = peak_time(wf, thN, phN)

# LAL peak time, refined on a spline of |h|
aL = np.abs(hL)
iL = int(np.argmax(aL))
sl = slice(iL - 3, iL + 4)
tt = np.linspace(tL[iL - 1], tL[iL + 1], 2001)
tL_star = float(tt[np.argmax(np.abs(CubicSpline(tL[sl], hL[sl])(tt)))])


def reldiff(h_ours_fn, shift):
    """||hL - h_ours|| / ||hL|| on the window, with our times shifted by `shift` (M)."""
    m = (tL >= tL_star + WIN[0]) & (tL <= tL_star + WIN[1])
    ho = h_ours_fn(tL[m] - shift)
    return float(np.linalg.norm(hL[m] - ho) / np.linalg.norm(hL[m]))


def ours(theta, phi):
    Y = wf.ylm_matrix(theta, phi)[0]
    return lambda t: wf.modes_at(t) @ Y


shift = tL_star - t_star
cases = {
    "N=(iota, pi/2-phase) [ours]": (thN, phN),
    "control: N=(iota, phase)": angles(unit_vector(p["iota"], p["phase"])),
    "control: N=(pi-iota, pi/2-phase)": (np.pi - p["iota"], np.pi / 2 - p["phase"]),
}
res = {name: {"aligned": reldiff(ours(*a), shift), "unaligned": reldiff(ours(*a), 0.0)}
       for name, a in cases.items()}

# Secondary: gwsurrogate's own inclination/phi_ref output (same model, its own mode sum)
sur = load_surrogate("NRSur7dq4")
tg, hg, _ = sur(p["mass_1"] / p["mass_2"], [p["spin_1x"], p["spin_1y"], p["spin_1z"]],
                [p["spin_2x"], p["spin_2y"], p["spin_2z"]], dt=0.1, f_low=0.0,
                f_ref=wf.f_ref_geom, inclination=p["iota"], phi_ref=p["phase"])
hg_spl = CubicSpline(tg, hg)
res["gwsurrogate inclination/phi_ref output (vs LAL)"] = {
    "aligned": reldiff(hg_spl, shift), "unaligned": reldiff(hg_spl, 0.0)}
m = (wf.t >= t_star + WIN[0]) & (wf.t <= t_star + WIN[1])
res["ours vs gwsurrogate own output"] = float(
    np.linalg.norm(wf.strain(thN, phN)[m] - hg_spl(wf.t[m])) / np.linalg.norm(hg_spl(wf.t[m])))

ok_main = res["N=(iota, pi/2-phase) [ours]"]["aligned"] < PASS
ok_ctrl = all(res[k]["aligned"] > FAIL for k in cases if k.startswith("control"))
out = {
    "script": "tasks/t01-merger-inclination/S2/gate.py",
    "src_commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                 text=True).stdout.strip(),
    "date": datetime.date.today().isoformat(),
    "input": {"file": PE, "label": LABEL, "index": p["index"], "f_ref_Hz": p["f_ref"]},
    "settings": {"fs_Hz": FS, "window_M": WIN, "pass": PASS, "control_fail": FAIL,
                 "surrogate": "gwsurrogate NRSur7dq4 (v1)", "lal": "NRSur7dq4, f_min=0"},
    "t_star_ours_M": t_star, "t_star_lal_M": tL_star, "peak_shift_M": shift,
    "lal_epoch_s": float(hp.epoch), "results": res,
    "gate_pass": bool(ok_main), "controls_fail_as_required": bool(ok_ctrl),
}
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out, indent=1))
