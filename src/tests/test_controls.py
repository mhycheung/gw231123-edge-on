"""S2 controls of t01 (plan.md): aligned spins, iota_Q at f_ref, helicity, quaternion direction.

Thresholds are the plan's, fixed before the runs, with two changes made on 2026-09-25 after
the plan's versions failed for reasons outside our code (tasks/t01-merger-inclination/subcontext/S2_controls.md):
- iota_Q constant for aligned spins to 1e-3 rad, not 1e-6: the surrogate's own q_copr has
  |q_x|, |q_y| up to 3.7e-4 for aligned-spin input (MEASURED).
- e = +z for aligned spins only where the odd-m modes vanish (q = 1, equal spins) or are
  removed: at q = 1.5 they tilt the instantaneous emission maximum by 5.6 deg (MEASURED). For
  q = 1.5 we test the equatorial reflection symmetry instead.
- For q = 1 equal spins, e = +z to 5e-3 rad, not 1e-3: the surrogate's odd-m modes are not
  exactly zero (|h21|/|h22| = 4.2e-4, |h33|/|h22| = 2.8e-4 at the peak, MEASURED) and tilt e
  by 1.2-2.1 mrad near the peak. The (2, +-2)-only test keeps 1e-3.
"""
E_SYM_TOL = 5e-3

import numpy as np
import pytest

from merger_inclination.frames import angle_between, angles, line_of_sight
from merger_inclination.inclination import (compute, emission_maxima, helicity, iota_Q,
                                            peak_time, z_copr)
from merger_inclination.waveform import Waveform, evaluate


def params(chiA, chiB, iota, phase, q=1.5, M=60.0, f_ref=20.0):
    m2 = M / (1 + q)
    return dict(mass_1=M - m2, mass_2=m2, spin_1x=chiA[0], spin_1y=chiA[1], spin_1z=chiA[2],
                spin_2x=chiB[0], spin_2y=chiB[1], spin_2z=chiB[2], iota=iota, phase=phase,
                f_ref=f_ref)


ALIGNED = params([0, 0, 0.5], [0, 0, 0.3], iota=0.7, phase=1.1)
ALIGNED_SYM = params([0, 0, 0.4], [0, 0, 0.4], iota=0.7, phase=1.1, q=1.0)
PRECESSING = params([0.6, -0.3, 0.2], [-0.2, 0.7, -0.1], iota=0.9, phase=0.4, q=1.2)
Z = np.array([0.0, 0, 1])


@pytest.fixture(scope="module")
def aligned():
    return compute(ALIGNED, series=False)


def test_a_aligned_iotaQ_constant(aligned):
    res, wf = aligned
    N = line_of_sight(ALIGNED["iota"], ALIGNED["phase"])
    iq = iota_Q(wf, N, wf.t)
    assert np.max(np.abs(iq - ALIGNED["iota"])) < 1e-3


def test_a_aligned_symmetric_emission_along_z():
    res, _ = compute(ALIGNED_SYM, series=False)
    assert angle_between(res["e"], Z) < E_SYM_TOL
    assert abs(res["iota_E"] - res["iota_Q"]) < E_SYM_TOL
    assert not res["helicity_ambiguous"]


def test_a_aligned_l2m2_only_emission_along_z(aligned):
    res, wf = aligned
    keep = [i for i, (l, m) in enumerate(wf.modes) if l == 2 and abs(m) == 2]
    w2 = Waveform(wf.t, [wf.modes[i] for i in keep], wf.H[:, keep], wf.q_copr, wf.orbphase,
                  wf.f_ref_geom, wf.t_ref, wf.model)
    assert angle_between(emission_maxima(w2, res["t_star_M"])["e"], Z) < 1e-3


def test_a_aligned_reflection_symmetry(aligned):
    """Aligned spins: h_{l,-m} = (-1)^l h_lm^*, so e_opp is e mirrored in the xy plane."""
    res, _ = aligned
    assert not res["helicity_ambiguous"]
    mirrored = np.array(res["e"]) * [1, 1, -1]
    assert angle_between(res["e_opp"], mirrored) < 1e-3


def test_b_precessing_iotaQ_at_fref():
    wf = evaluate(PRECESSING)
    N = line_of_sight(PRECESSING["iota"], PRECESSING["phase"])
    assert abs(iota_Q(wf, N, wf.t_ref) - PRECESSING["iota"]) < 1e-3


@pytest.mark.parametrize("iota,sign", [(0.0, -1), (np.pi, +1)])
def test_c_face_on_helicity(iota, sign):
    p = dict(ALIGNED, iota=iota)
    wf = evaluate(p)
    N = line_of_sight(iota, p["phase"])
    ts = peak_time(wf, *angles(N))
    assert np.sign(helicity(wf, N, ts)) == sign
    if iota == 0.0:
        ws = evaluate(dict(ALIGNED_SYM, iota=0.0))
        ts_s = peak_time(ws, *angles(N))
        assert angle_between(emission_maxima(ws, ts_s)["e"], Z) < E_SYM_TOL


def test_quaternion_direction():
    """z_copr = R(q) z must follow the emission axis during the inspiral; R(q)^T z must not."""
    wf = evaluate(PRECESSING)
    t = wf.t[0] + 500.0
    e = emission_maxima(wf, t)["e"]
    right = angle_between(e, z_copr(wf, t))
    w, x, y, zq = wf.quat_at(t)
    wrong_axis = np.array([2 * (x * zq - w * y), 2 * (y * zq + w * x), 1 - 2 * (x * x + y * y)])
    wrong = angle_between(e, wrong_axis)
    tilt = angle_between(z_copr(wf, t), Z)
    print(f"t={t:.1f} tilt={np.degrees(tilt):.2f} deg right={np.degrees(right):.3f} "
          f"wrong={np.degrees(wrong):.3f} deg")
    assert np.degrees(right) < 2.0
    assert wrong > 3 * right
