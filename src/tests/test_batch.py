"""t02 batch function on an aligned, equal-mass case (thresholds from test_controls.py)."""
import numpy as np

from merger_inclination.batch import T_E, T_Q, sample_inclination
from test_controls import ALIGNED_SYM, E_SYM_TOL


def test_grids():
    assert T_Q[0] == -4300 and T_Q[-1] == 100 and len(T_E) == 91 and 0.0 in T_E


def test_aligned_sample():
    r = sample_inclination(ALIGNED_SYM)
    iq = r["iota_Q"][np.isfinite(r["iota_Q"])]
    assert iq.size > 1000
    assert np.max(np.abs(iq - ALIGNED_SYM["iota"])) < 1e-3
    assert np.max(np.abs(r["iota_E"] - ALIGNED_SYM["iota"])) < E_SYM_TOL
    assert np.all(r["helicity_E"] < 0)
