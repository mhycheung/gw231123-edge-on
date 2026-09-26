# Project context: Is GW231123 edge-on at merger?

Last updated: 2026-09-25

<!-- The state of the project now, edited in place by the main agent. At most 200 lines.
Test for every edit: could a fresh agent, given only AGENTS.md and this file, take the
correct next action without asking anything? History goes in log/, not here. -->

## Goal

<!-- Two lines. -->

## Tasks

| id | status | what | pointer |
|---|---|---|---|
| t03-mismatch-volume | done | Mismatch-metric volume per unit prior probability vs $\iota_Q(0)$. Edge-on at merger: ratio of medians $R_{\rm edge}=18$ (16–20), not rising with $\chi_p$, though median $s$ rises with $\chi_p$ (milestone figure); tracks weak network signal; posterior samples 1.13 | `tasks/t03-mismatch-volume/context.md` |
| t02-posterior-inclination | done | iota_Q(t), iota_E(t) over the NRSur posterior and prior. Posterior median \|iota_Q - 90\| 39 deg at f_ref, 12.6 deg at t = 0; P(within 20 deg of edge-on at t = 0) 0.82 vs prior 0.33 | `tasks/t02-posterior-inclination/context.md` |
| t01-merger-inclination | done | Orbital inclination at peak strain from NRSur7dq4v2, applied to GW231123. ML sample: iota 64 deg at f_ref, iota_Q 82-90 deg at the near-equal strain peaks | `tasks/t01-merger-inclination/context.md` |

## In flight

Nothing.

## Next step

No task active. Wait for the user's answers to the t03 questions below and the choice of the next task (candidate: the residual-absorption test named in t03 `plan.md`, "Limits").

## Waiting on the user

- t01: report iota at a single t*, or the iota_Q range over the three near-equal peaks of
  |h| (82-90 deg)? Asked on Slack 2026-09-25. See `tasks/t01-merger-inclination/context.md`.
- t02: main band plot as |iota - 90 deg| or iota as planned? Asked on Slack 2026-09-25.
- t03: review two deviations from the S1 gate wording (`tasks/t03-mismatch-volume/S1/controls.md`); deviation 2 closed in S3.
- t03: headline statistic (ratio of medians, chosen, vs the plan's ratio of means), whether to add the distance-weighted score, and `milestone` for `r-t03-edge-on-metric-volume` (the user made the $s$ vs $|\cos\iota_Q(t_{\rm peak})|$ figure a milestone instead, 2026-09-25). See `tasks/t03-mismatch-volume/context.md`, "Open questions". Posted to the Feed 2026-09-25.
- Whether to commit `lit_cache/1905.09300/` and `lit_cache/2609.07873/` (28 MB, untracked).

## Open questions

None.

## Rules in force

<!-- Rule ids from rules/README.md that apply to current work, e.g. "R01, R03". -->
