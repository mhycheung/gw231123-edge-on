---
status: done
---

# S1 test run (2026-09-25)

Test chunks in `data/t02-posterior-inclination/test/` (posterior 0-99 and 6096, prior 0-99),
run in the main agent's allocation. Gate: `S1/gate_2026-09-25.json` — PASS.

- (a) ML sample iota_Q(0) = 88.71503841002698 deg = t01 value (diff 0); control N = (iota, phase): 47.64 deg (fails as required).
- (b) max |iota_Q(t_ref) - iota| = 3.8e-4 rad (post), 3.9e-4 rad (prior), after the t_ref fix (`subcontext/S1_tref.md`; first run failed at 0.021 rad).
- (c) 0 failures of 201.
- (d) tracked e vs fresh full-sphere search at t = -100, -1000 M: 42/42 within 0.1 deg (worst 0.013 deg).
- (e) 5.9 s per sample (MEASURED mean) -> 38 CPU-h for 23185 samples; chunk size 150 (~15 min).
- Tracked-axis helicity positive (other maximum) at 0.46 % of prior (sample, time) points, 0 % posterior.
