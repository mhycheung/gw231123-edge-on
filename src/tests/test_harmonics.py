import numpy as np
from gwtools.harmonics import sYlm as ref_sYlm

from merger_inclination.waveform import sYlm


def test_sylm_matches_gwtools():
    rng = np.random.default_rng(1)
    th = np.concatenate([[0.0, np.pi, 1e-3], rng.uniform(0, np.pi, 30)])
    ph = rng.uniform(0, 2 * np.pi, th.size)
    err = 0.0
    for l in range(2, 6):
        for m in range(-l, l + 1):
            mine = sYlm(-2, l, m, th, ph)
            ref = np.array([ref_sYlm(-2, l, m, a, b) for a, b in zip(th, ph)])
            err = max(err, np.max(np.abs(mine - ref)))
    assert err < 1e-12, err
