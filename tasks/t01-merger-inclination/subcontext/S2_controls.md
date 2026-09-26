# S2: convention gate and controls (2026-09-25)

## Gate (plan thresholds, unchanged): PASS

`pixi run python tasks/t01-merger-inclination/S2/gate.py tasks/t01-merger-inclination/S2/gate_2026-09-25.json`
(src at a37549c plus the uncommitted S2 code, committed right after). MEASURED:

| comparison over [t* - 500 M, t* + 50 M], vs LAL NRSur7dq4 h+ - i hx | rel. L2 |
|---|---|
| ours, N = (iota, pi/2 - phase), gwsurrogate NRSur7dq4 v1 | 6.4e-5 |
| control N = (iota, phase) | 1.62 |
| control N = (pi - iota, pi/2 - phase) | 1.40 |
| gwsurrogate's own inclination/phi_ref output | 6.4e-5 |
| ours vs gwsurrogate's own output | 3.9e-16 |

The peak times agree to 3.5e-5 M (t* = -2.692 M for v1), so LAL and gwsurrogate share
the time origin. The result: gwsurrogate modes live in the LAL source frame at f_ref, and
N = (iota, pi/2 - phase) is the line of sight the PE used.

## Controls (`pixi run pytest -q src/tests`, 9 passed)

Three plan thresholds failed for reasons outside our code and were changed after the
failure; each change is backed by a measurement:

1. **Aligned spins, iota_Q(t) constant: 1e-6 -> 1e-3 rad.** Deviation 8.9e-4 rad max (3.3e-4
   before t = -100 M). The surrogate's own q_copr has |q_x|, |q_y| up to 3.7e-4 for
   aligned-spin input (MEASURED), which accounts for it (tilt ~ 2|q_xy|).
2. **Aligned spins, e = +z fails at q = 1.5 by 5.59 deg.** Cause, tested: the odd-m modes
   ((2,1), (3,3), ...) vanish at theta = 0 but grow linearly with theta and interfere with (2,2), so
   the instantaneous |h(n)| is lopsided in azimuth. Evidence: keeping only (2, +-2) gives
   1e-5 deg; q = 1 equal spins (odd-m modes zero by symmetry) gives 0.02 deg; the tilt is
   3.3 deg at t* - 500 M and 5.6 deg at t*. Replaced by: e = +z at q = 1 (tol 5e-3 rad, see 3),
   e = +z with (2, +-2) only (1e-3 rad), and the equatorial reflection symmetry at q = 1.5
   (e_opp = mirror of e, 1e-3 rad).
3. **q = 1 equal spins, e = +z to 1e-3 rad fails by 1.7e-3 rad.** The surrogate's odd-m modes
   are not exactly zero there: |h21|/|h22| = 4.2e-4, |h33|/|h22| = 2.8e-4 at the peak (MEASURED).
   Tolerance 5e-3 rad.

Added control (must fail, fails): quaternion direction. At t = t0 + 500 M of a precessing
case (L tilted 6.97 deg from z), angle(e, R(q) z) = 0.94 deg, angle(e, R(q)^T z) = 14.6 deg.

Passed at plan thresholds: (b) iota_Q(t_ref) = iota to 1e-3 rad for a precessing case;
(c) helicity at N negative for iota = 0 and positive for iota = pi; harmonics vs gwtools to
1e-12.

## Consequence for the result (inference, to state in the report)

Method 2 (direction of maximum emission) measures the instantaneous beaming direction. For
unequal masses or asymmetric spins it is tilted from the orbital axis by the odd-m modes,
several degrees at q = 1.5, with a direction that turns with the orbital phase. So iota_E -
iota_Q contains this beaming offset as well as any difference between the coprecessing axis and
the true orbital axis. GW231123's ML sample has q = 1.10 but large in-plane spins.
