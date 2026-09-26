"""Constants of the t03 metric calculation, declared once with their source (R04).

Sources: `tasks/t03-mismatch-volume/plan.md` (design choices) and the PE file
`data/t01-merger-inclination/posterior_samples.h5`, label `C00:NRSur7dq4` (values marked PE;
`check_pe_constants` re-reads them and asserts).
"""

import numpy as np

PE_FILE = "data/t01-merger-inclination/posterior_samples.h5"
LABEL = "C00:NRSur7dq4"
ML_INDEX = 6096            # argmax of log_likelihood (PE), asserted in check_pe_constants

# Likelihood settings (PE config_file/config)
APPROXIMANT = "NRSur7dq4"  # LAL approximant; gwsurrogate model of the same name (v1)
DURATION = 8.0             # s
SAMPLING_FREQUENCY = 1024.0
POST_TRIGGER = 2.0         # s; data start = trigger_time + 2 - 8
TRIGGER_TIME = 1384782888.634277
F_REF = 10.0               # Hz
F_MIN_WF = 0.0             # waveform start frequency ('waveform: 0')
F_MIN = 20.0               # likelihood band, both detectors
F_MAX = 448.0
DETECTORS = ("H1", "L1")
DELTA_T = 1.0 / 1024       # s; LAL SimInspiralFD's choice for f_max = 448 Hz (0.5/f_max
                           # rounded down to a power of 2), reproduced in metric.polarizations
# Tapers in continuous time, units of M (S1 debugging, S1/controls.md): Planck start taper over
# the first 145 M (median of LAL's TAPER_START length at the 20 check points, 100-185 M), cos^2
# end taper from 60 M to 95 M after t = 0 (the surrogate ends at 100 M).
TAPERS_M = (145.0, 60.0, 95.0)

# Coordinates x (plan.md, "Coordinates for derivatives")
X_NAMES = ("M", "q", "chi1x", "chi1y", "chi1z", "chi2x", "chi2y", "chi2z",
           "iota", "phi_ref", "psi", "t_c")
THETA_NAMES = ("M", "q", "chi1x", "chi1y", "chi1z", "chi2x", "chi2y", "chi2z", "iota_Q0")
I_IOTA, I_PHI, I_PSI, I_TC = 8, 9, 10, 11

# Finite differences for the first 10 coordinates (units of x); S1 (d), S1/controls.md.
# Waveform: pilot steps STEPS (second order) give g_kk; final step FD_DELTA / sqrt(g_kk), at
# most STEP_MAX, fourth order. iota_Q(0): fixed steps K_STEPS, second order.
STEPS = np.array([0.05, 1e-3, 2e-3, 2e-3, 2e-3, 2e-3, 2e-3, 2e-3, 2e-3, 2e-3])
FD_DELTA = 0.0125
STEP_MAX = np.array([1.0, 0.01, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.05, 0.05])
K_STEPS = np.array([0.05, 5e-4, 5e-4, 5e-4, 5e-4, 5e-4, 5e-4, 5e-4, 1e-3, 1e-3])
A_MAX = 0.99               # PE prior spin-magnitude maximum; one-sided differences within a step
Q_MAX = 1.0                # q = m2/m1 <= 1 (bilby convention); one-sided above

# Numerics
PINV_RCOND = 1e-10         # relative cutoff for C^+ (plan.md), on the Jacobi-scaled C
SUR_DT = 1.0               # time step (M) of the gwsurrogate call for iota_Q(0); S1 check (b)

# Point sets (plan.md, "Point sets"); window = posterior 5-95 % (PE, MEASURED in S1)
M_WINDOW = (287.0, 333.2)  # Msun, detector frame
Q_WINDOW = (0.685, 0.974)
N_WIN = 8000
N_POST = 2000              # plus ML_INDEX
SEED = 1

# Secondary quantities
RHO = 20.6                 # median network matched-filter SNR (PE: 20.646)
# Prior standard deviations of theta in the window (for N_rho). Spin component: a ~ U(0, 0.99),
# isotropic: std = 0.99/3. iota_Q(0) ~ sine: std = sqrt(pi^2/4 - 2). M, q: from the window
# density M/(1+q)^2 on the rectangle, computed in S1 (window_std).
SPIN_COMPONENT_STD = A_MAX / 3
IOTA_STD = float(np.sqrt(np.pi ** 2 / 4 - 2))
# Nuisance prior standard deviations: phi_ref ~ U(0, 2 pi), psi ~ U(0, pi), t_c ~ U(0.2 s).
NU_STD = {"phi_ref": 2 * np.pi / np.sqrt(12), "psi": np.pi / np.sqrt(12),
          "iota": IOTA_STD, "t_c": 0.2 / np.sqrt(12)}
CHI_P_BINS = (0.0, 0.4, 0.7, 1.0)
N_COS_BINS = 6


def window_std():
    """Standard deviations of M and q under the prior density M/(1+q)^2 on the window."""
    M = np.linspace(*M_WINDOW, 2001)
    q = np.linspace(*Q_WINDOW, 2001)
    MM, QQ = np.meshgrid(M, q, indexing="ij")
    w = MM / (1 + QQ) ** 2
    w /= w.sum()
    sd = lambda a: float(np.sqrt((w * a ** 2).sum() - (w * a).sum() ** 2))
    return sd(MM), sd(QQ)


def check_pe_constants(path=PE_FILE):
    """Re-read the PE values quoted above and assert them."""
    import h5py
    from merger_inclination.params import _scalar
    with h5py.File(path, "r") as f:
        g = f[LABEL]
        c = g["config_file/config"]
        ps = g["posterior_samples"][()]
        assert int(np.argmax(ps["log_likelihood"])) == ML_INDEX
        assert float(_scalar(c["duration"])) == DURATION
        assert float(_scalar(c["sampling_frequency"])) == SAMPLING_FREQUENCY
        assert float(_scalar(c["post_trigger_duration"])) == POST_TRIGGER
        assert abs(float(_scalar(c["trigger_time"])) - TRIGGER_TIME) < 1e-6
        assert float(_scalar(c["reference_frequency"])) == F_REF
        assert _scalar(c["waveform_approximant"]) == APPROXIMANT
        assert _scalar(c["maximum_frequency"]).replace(" ", "") == "{H1:448,L1:448,}"
        assert _scalar(c["minimum_frequency"]).replace(" ", "") == "{H1:20,L1:20,waveform:0}"
        M = ps["mass_1"] + ps["mass_2"]
        q = ps["mass_2"] / ps["mass_1"]
        assert np.allclose(np.percentile(M, [5, 95]), M_WINDOW, atol=0.05)
        assert np.allclose(np.percentile(q, [5, 95]), Q_WINDOW, atol=5e-4)
        assert abs(np.median(ps["network_matched_filter_snr"]) - RHO) < 0.05
    return True
