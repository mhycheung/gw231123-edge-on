---
id: t02-posterior-inclination
title: Inclination vs time over the GW231123 NRSur posterior and prior
short_name: posterior-incl
type: task
status: done
depends_on:
- t01-merger-inclination
privacy: public
summary: 'Done: over all 18185 posterior samples the median |iota_Q - 90 deg| falls from 39 deg at f_ref to 12.6 deg at t = 0; P(|iota_Q(0) - 90| < 20 deg) = 0.82 vs 0.33 for the prior, whose distribution is time-independent (control). S3/results.md.'
verification: unverified
---

# Inclination vs time over the GW231123 NRSur posterior and prior

<!-- opsci:node-table: generated from the front matter by `opsci map build`; edit the front matter, not this table -->

| task | `t02-posterior-inclination` |
|---|---|
| **short name** | `posterior-incl` |
| **status** | done |
| **privacy** | public |
| **verification** | unverified |
| **depends on** | `t01-merger-inclination` |
| **summary** | Done: over all 18185 posterior samples the median \|iota_Q - 90 deg\| falls from 39 deg at f_ref to 12.6 deg at t = 0; P(\|iota_Q(0) - 90\| < 20 deg) = 0.82 vs 0.33 for the prior, whose distribution is time-independent (control). S3/results.md. |

<!-- /opsci:node-table -->

Last updated: 2026-09-25

## Goal

Credible bands of iota_Q(t) and iota_E(t) against t/M, and their distributions at t = 0, for
the GW231123 `C00:NRSur7dq4` posterior and prior, with NRSur7dq4v2 and the t01 code. Full
spec: `plan.md`.

## Current state

Done 2026-09-25. S1 gate passed (`S1/test_run.md`, t_ref fix in `subcontext/S1_tref.md`).
S2: job array 20907281, 156/156 chunks, 0 failed samples of 18185 + 5000, 36.0 CPU-h
(`S2/run.md`). S3: aggregated arrays `data/t02-posterior-inclination/{post,prior}_2026-09-25.npz`,
numbers `S3/summary_2026-09-25.json`, figures and reading in `S3/results.md`,
`S3/provenance.yaml`. Sent to the owner on Slack 2026-09-25.

Result (MEASURED): the posterior median |iota_Q - 90 deg| is 39.0 deg at f_ref and 12.6 deg at
t = 0 (minimum 8.2 deg at t = -12 M); P(|iota_Q(0) - 90| < 20 deg) = 0.82 posterior, 0.33
prior. The prior distribution does not change with time (control). The posterior iota is
bimodal about 90 deg, so the planned band plot of iota has a misleading median; a
supplementary plot of |iota - 90 deg| (`S3/folded_bands_2026-09-25.png`) was added.

## In flight

Nothing.

## Next step

None in this task. Possible follow-ups (not started): check why iota_Q is constant for
t > ~+20 M in every sample; the helicity flips of the tracked iota_E in 11.3 % of prior samples.

## Open questions

- Owner: main band plot = |iota - 90 deg| (supplementary figure) or iota as planned? Asked on
  Slack 2026-09-25. Both files exist.

## Pointers

- Plan: `plan.md`. Code and conventions: t01 (`tasks/t01-merger-inclination/context.md`,
  `subcontext/S2_controls.md` there for what the controls established).
