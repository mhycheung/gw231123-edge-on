---
id: t01-merger-inclination
title: Orbital inclination at peak strain from NRSur7dq4v2
short_name: merger-incl
type: task
status: done
privacy: public
summary: 'Done 2026-09-25. GW231123 NRSur ML sample (iota = 64.3 deg at f_ref = 10 Hz): iota_Q rises to a maximum of 89-90 deg at t ~ -6 M; at t* iota_Q = 81.8 deg (v2, t* = -27 M) or 89.8 deg (v1, t* = -2.7 M), because three near-equal peaks of |h| make t* unstable. Convention gate vs LAL passes (6e-5).'
verification: unverified
---

# Orbital inclination at peak strain from NRSur7dq4v2

<!-- opsci:node-table: generated from the front matter by `opsci map build`; edit the front matter, not this table -->

| task | `t01-merger-inclination` |
|---|---|
| **short name** | `merger-incl` |
| **status** | done |
| **privacy** | public |
| **verification** | unverified |
| **summary** | Done 2026-09-25. GW231123 NRSur ML sample (iota = 64.3 deg at f_ref = 10 Hz): iota_Q rises to a maximum of 89-90 deg at t ~ -6 M; at t* iota_Q = 81.8 deg (v2, t* = -27 M) or 89.8 deg (v1, t* = -2.7 M), because three near-equal peaks of \|h\| make t* unstable. Convention gate vs LAL passes (6e-5). |

<!-- /opsci:node-table -->

Last updated: 2026-09-25

<!-- The state of this task now, edited in place. At most 200 lines. A fresh agent given
AGENTS.md, the project context.md and this file must be able to take the correct next
action. Detail and history go in subcontext/ and log.md. -->

## Goal

Code in `src/merger_inclination/` giving the orbital inclination at the peak of |h_+ - i h_x|
along the line of sight, by (1) the NRSur7dq4v2 coprecessing-frame axis and (2) the direction
of maximum emission; applied to the GW231123 NRSur maximum-likelihood sample. Full spec: `plan.md`.

## Current state

All three subtasks done 2026-09-25; the plan's done criteria are met; plots and summary sent
to the owner on Slack. Waiting for the owner's reply to the question below.

Result (MEASURED; `S3/result_*.json`, `S3/peak_candidates_2026-09-25.json`, `S3/provenance.yaml`):
ML sample index 6096 of `C00:NRSur7dq4`, iota = 64.3 deg at f_ref = 10 Hz (t_ref = -196 M).

| model | t* (M) | iota_Q (deg) | iota_E (deg) |
|---|---|---|---|
| NRSur7dq4v2 | -27.0 | 81.8 | 80.4 |
| NRSur7dq4 (v1) | -2.7 | 89.8 | 88.6 |

- |h(t, N)| has three peaks within 1-9 % of each other, at t = -27, -13, -3 M; the models agree
  at each (iota_Q 82, 87-88, 89-90 deg) but pick different ones as highest (margins 1-2 %).
- Maximum of iota_Q(t < 20 M): 89.1 deg (v2), 90.0 deg (v1), at t ~ -6 M. iota_Q(-1000 M) = 85 deg:
  f_ref sits near a minimum of iota_Q.
- iota_E contains a beaming offset from the odd-m modes (5.6 deg for an aligned q = 1.5 case);
  see `subcontext/S2_controls.md`.
- Both spins (0.96, 0.99) are outside the surrogate training range (<= 0.8); the PE used the
  same extrapolated model.

Checks: convention gate vs LAL NRSur7dq4 rel. L2 6.4e-5, must-fail controls 1.62 and 1.40
(`S2/gate_2026-09-25.json`); `pixi run pytest -q` 9 passed (3 plan thresholds changed with
evidence, `subcontext/S2_controls.md`).

## In flight

Nothing.

## Next step

Wait for the owner's answer. Nothing else is planned in this task. A follow-up (the same
calculation over posterior samples) would be a new task.

## Open questions

- Owner: report iota at a single t*, or the iota_Q range over the three near-equal peaks
  (82-90 deg)? Asked on Slack 2026-09-25.
- What "CC" and "RR" mean in the GWOSC labels of the two Zenodo versions. The task used the
  newer record (17437902); it holds one NRSur label.

## Pointers

- Plan: `plan.md`. Inputs: `S1/inputs.md` (read to rerun). Gate and controls:
  `subcontext/S2_controls.md` (read before changing the code or tests).
- Rerun: `bash tasks/t01-merger-inclination/S1/setup_data.sh`, then the commands in
  `S3/provenance.yaml`. Series data (41 MB): `data/t01-merger-inclination/S3/`.
- Sources: `lit_cache/2609.07873/`, `lit_cache/1905.09300/` (untracked; the owner decides
  whether to commit them).
