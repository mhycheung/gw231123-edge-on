"""S1 control: the PE prior in (theta_jn, phi_jl, tilts, phi_12, phase) equals isotropic
Cartesian spins in the LAL L-n frame at f_ref and an isotropic line of sight (iota, phi_ref),
independent of each other. Stored prior samples converted with LAL; KS tests against the claim,
and the same tests on a deliberately wrong prior (theta_jn uniform instead of sine) as the
control that must fail."""
import h5py, json, numpy as np, lal, lalsimulation as ls
from scipy import stats
from mismatch_metric import defaults as D

import sys
g = h5py.File(D.PE_FILE)[D.LABEL]["priors/samples"]
P = {k: g[k][()] for k in ("theta_jn", "phi_jl", "tilt_1", "tilt_2", "phi_12", "a_1", "a_2",
                           "mass_1", "mass_2", "phase")}
n = len(P["a_1"])
FRESH = len(sys.argv) > 1   # fresh draws from the same prior forms (PE config prior_dict)
if FRESH:
    r0 = np.random.default_rng(2)
    n = int(sys.argv[1])
    j = r0.integers(0, len(P["a_1"]), n)
    sine = lambda: np.arccos(r0.uniform(-1, 1, n))
    P = {"theta_jn": sine(), "tilt_1": sine(), "tilt_2": sine(),
         "phi_jl": r0.uniform(0, 2 * np.pi, n), "phi_12": r0.uniform(0, 2 * np.pi, n),
         "phase": r0.uniform(0, 2 * np.pi, n), "a_1": r0.uniform(0, 0.99, n),
         "a_2": r0.uniform(0, 0.99, n), "mass_1": P["mass_1"][j], "mass_2": P["mass_2"][j]}

def convert(theta_jn):
    out = np.zeros((n, 7))
    for i in range(n):
        out[i] = ls.SimInspiralTransformPrecessingNewInitialConditions(
            theta_jn[i], P["phi_jl"][i], P["tilt_1"][i], P["tilt_2"][i], P["phi_12"][i],
            P["a_1"][i], P["a_2"][i], P["mass_1"][i] * lal.MSUN_SI, P["mass_2"][i] * lal.MSUN_SI,
            D.F_REF, P["phase"][i])
    return out

def tests(c):
    iota, s1, s2 = c[:, 0], c[:, 1:4], c[:, 4:7]
    phi = P["phase"]
    N = np.column_stack([np.sin(iota) * np.cos(np.pi / 2 - phi), np.sin(iota) * np.sin(np.pi / 2 - phi), np.cos(iota)])
    u1 = s1 / np.linalg.norm(s1, axis=1)[:, None]
    u2 = s2 / np.linalg.norm(s2, axis=1)[:, None]
    U = lambda v, lo, hi: stats.kstest(v, "uniform", args=(lo, hi - lo)).pvalue
    az = lambda u: np.mod(np.arctan2(u[:, 1], u[:, 0]), 2 * np.pi)
    return {
        "cos_iota_uniform": U(np.cos(iota), -1, 1),
        "u1z_uniform": U(u1[:, 2], -1, 1), "u2z_uniform": U(u2[:, 2], -1, 1),
        "u1_azimuth_uniform": U(az(u1), 0, 2 * np.pi), "u2_azimuth_uniform": U(az(u2), 0, 2 * np.pi),
        # independence of N and spins: N.u1, N.u2 uniform on [-1, 1] if N isotropic and independent
        "N_dot_u1_uniform": U(np.sum(N * u1, 1), -1, 1), "N_dot_u2_uniform": U(np.sum(N * u2, 1), -1, 1),
        "u1_dot_u2_uniform": U(np.sum(u1 * u2, 1), -1, 1),
        # the rotation about L: azimuth of N minus azimuth of u1 uniform
        "az_N_minus_az_u1_uniform": U(np.mod(np.pi / 2 - phi - az(u1), 2 * np.pi), 0, 2 * np.pi),
        "corr_cos_iota_u1z_pvalue": stats.pearsonr(np.cos(iota), u1[:, 2]).pvalue,
    }

res = {"n": n, "pe_prior": tests(convert(P["theta_jn"]))}
rng = np.random.default_rng(1)
res["control_theta_jn_uniform"] = tests(convert(rng.uniform(0, np.pi, n)))
print(json.dumps(res, indent=1))
name = f"check_prior_fresh{n}" if FRESH else "check_prior"
json.dump(res, open(f"tasks/t03-mismatch-volume/S1/{name}_2026-09-25.json", "w"), indent=1)
