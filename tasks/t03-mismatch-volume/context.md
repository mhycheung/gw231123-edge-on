---
id: t03-mismatch-volume
title: Density of distinguishable waveforms vs inclination at merger
short_name: mismatch-vol
type: task
status: done
depends_on:
- t02-posterior-inclination
- t01-merger-inclination
privacy: public
summary: 'Done 2026-09-25. Edge-on orientations at merger have more distinguishable NRSur7dq4 waveforms per unit prior probability near GW231123: ratio of medians $R_{\rm edge}=18$ (68 %: 16-20), not rising with $\chi_p$, although the median of $s$ rises with $\chi_p$ by 2.2-2.8 decades at every inclination (milestone figure); the ratio of means is not converged. The excess tracks weak network signal ($\sqrt{\det g}\propto\langle h,h\rangle^{-4.5}$ when only $\psi$ changes). Among posterior samples the ratio is 1.13.'
verification: unverified
---

# Density of distinguishable waveforms vs inclination at merger

<!-- opsci:node-table: generated from the front matter by `opsci map build`; edit the front matter, not this table -->

| task | `t03-mismatch-volume` |
|---|---|
| **short name** | `mismatch-vol` |
| **status** | done |
| **privacy** | public |
| **verification** | unverified |
| **depends on** | `t02-posterior-inclination`, `t01-merger-inclination` |
| **summary** | Done 2026-09-25. Edge-on orientations at merger have more distinguishable NRSur7dq4 waveforms per unit prior probability near GW231123: ratio of medians $R_{\rm edge}=18$ (68 %: 16-20), not rising with $\chi_p$, although the median of $s$ rises with $\chi_p$ by 2.2-2.8 decades at every inclination (milestone figure); the ratio of means is not converged. The excess tracks weak network signal ($\sqrt{\det g}\propto\langle h,h\rangle^{-4.5}$ when only $\psi$ changes). Among posterior samples the ratio is 1.13. |

<!-- /opsci:node-table -->

Last updated: 2026-09-25

<!-- The state of this task now, edited in place. At most 200 lines. A fresh agent given
AGENTS.md, the project context.md and this file must be able to take the correct next
action. Detail and history go in subcontext/ and log.md. -->

## Goal

Measure the density of distinguishable NRSur7dq4 waveforms per unit prior probability against $\iota_Q(0)$ and $\chi_p$ near GW231123,
and the edge-on ratio $R_{\rm edge}$; a necessary-condition test of the hypothesis that edge-on fits reflect waveform flexibility. Full spec: `plan.md`.

## Current state

**Done 2026-09-25** (plan's done criteria met: S1 gate passed with two deviations, 100 % of points evaluated, S3 figures, numbers,
result files). S1: `S1/controls.md`. S2: job 20909319, 10 001 points, 0 failures, 3.7 CPU-h (`S2/run.md`). S3: `S3/results.md`.

Results (MEASURED, `S3/summary_2026-09-25.json`):
- `results/r-t03-edge-on-metric-volume.md`: set W (8000 window prior draws) ratio of medians $R_{\rm edge}=18.0$ (68 %: 16.1–20.4); by $\chi_p$
  bin 20.7, 16.5, 12.2 (does not rise). The plan's ratio of means, $1.9\times10^3$, is not converged (the 10 largest points hold 91 % of the
  edge-on sum; the first 400 points give 7.4). Set P (posterior): ratio of medians 1.13 (1.03–1.21).
- `results/r-t03-signal-norm-mechanism.md`: large $s$ comes from orientations with weak network signal; varying $\psi$ alone gives
  $\sqrt{\det g^\theta}\propto\langle h,h\rangle^{-3.8\ {\rm to}\ -4.5}$ (3 points). Added to the plan in S3 to explain the heavy tail.
- `results/r-t03-s-vs-inclination-figure.md` (**milestone**, the user's request 2026-09-25): figure 1 remade with axis
  $|\cos\iota_Q(t_{\rm peak})|$ (`S3/fig1_s_vs_cos_W_tpeak_2026-09-25.png`, `S3/fig1_tpeak.py`). In the median, $s$ rises with $\chi_p$
  at every inclination: $\chi_p\ge0.7$ over $\chi_p<0.4$ is 2.2–2.8 decades, of which 0.8–1.2 from $\sqrt{\det g^\theta}$, the rest from
  $1/\pi_\theta\propto a_1^2a_2^2$ (`S3/chi_p_trend_2026-09-25.json`). The rise is similar at all inclinations, so $R_{\rm edge}$ does not rise.
- S1 deviation 2 closed: halved steps change the 400-point ratio of medians from 6.93 to 6.66.

## In flight

Nothing.

## Next step

None within this task, until the user answers the questions below. Answers may change the headline (a new result file, not an
overwrite). Follow-up not in this task: the residual-absorption test (plan, "Limits").

## Open questions

- For the user (posted to the Feed 2026-09-25): (1) lead with the ratio of medians (18) rather than the plan's ratio of means,
  which is not converged? Chosen: medians, with the means reported. (2) Report the score with the distance prior marginalised at
  fixed SNR, $s/\langle h,h\rangle^{3/2}$ (ratio of medians 119 W, 7.1 P), as well or instead? Chosen: supplementary only. (3) `milestone: true`
  for `r-t03-edge-on-metric-volume`? Left unset; the user made the figure a milestone instead (`r-t03-s-vs-inclination-figure`).
- For the user (posted 2026-09-25; chosen option in force): two deviations from the S1 gate wording, `S1/controls.md`.
  (1) check (c) literal at $10^{-3}$ fails (63 %) from cubic terms; gate taken as the symmetric test (90.4 %) and the literal
  test at $10^{-4}$ (92.6 %). (2) check (d) 18/20 within 0.05; closed by the S3 step check above.

## Pointers

- Plan: plan.md — the authority for this task.
- S1 record: S1/controls.md — read before changing `src/mismatch_metric/`.
- S2 record: S2/run.md — the run, failures (none).
- S3 record: S3/results.md — all numbers, files, what was added to the plan.
