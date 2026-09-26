---
id: r-t02-near-edge-on-at-merger
title: 'GW231123 is close to edge-on at merger: $P(|\iota_Q(0) - 90^\circ| < 20^\circ) = 0.82$, against 0.33 for the prior'
type: result
kind: value
status: done
milestone: true
depends_on: [r-t02-inclination-bands, r-t01-nrsur-extrapolation, r-t01-peak-ambiguity]
uses: [GW231123PE2025, Ravishankar2026]
artifacts:
  - tasks/t02-posterior-inclination/S3/t0_hist_2026-09-25.png
  - tasks/t02-posterior-inclination/S3/summary_2026-09-25.json
  - data/t02-posterior-inclination/post_2026-09-25.npz
  - data/t02-posterior-inclination/prior_2026-09-25.npz
code: [src/merger_inclination/batch.py, tasks/t02-posterior-inclination/S3/aggregate.py]
summary: 'Over the 18185 C00:NRSur7dq4 posterior samples, the median $|\iota_Q - 90^\circ|$ falls from $39.0^\circ$ at $f_{\rm ref}$ to $12.6^\circ$ at $t = 0$ (minimum $8.2^\circ$ at $t = -12\,M$). $P(|\iota_Q(0) - 90^\circ| < 20^\circ) = 0.82$ (posterior) vs 0.33 (prior); at $f_{\rm ref}$ the posterior value is 0.027. The prior distribution does not change with time.'
verification: unverified
evidence: tasks/t02-posterior-inclination/S3/provenance.yaml
---

# GW231123 is close to edge-on at merger

![](../S3/t0_hist_2026-09-25.png)

MEASURED from `S3/summary_2026-09-25.json` (`pixi run python
tasks/t02-posterior-inclination/S3/aggregate.py`; `S3/provenance.yaml`). Degrees; median
[5 %, 95 %].

| quantity | posterior | prior |
|---|---|---|
| $\iota$ at $f_{\rm ref}$ | 59.2 [35.3, 137.5] | 90.9 [26.6, 154.6] |
| $\iota_Q(0)$ | 82.3 [60.7, 109.3] | 91.0 [26.8, 154.5] |
| $\iota_E(0)$ | 82.7 [59.3, 110.4] | 91.3 [26.3, 154.7] |
| $P(\lvert\iota - 90\rvert < 20)$: $f_{\rm ref}$ / $\iota_Q(0)$ / $\iota_E(0)$ | 0.027 / 0.823 / 0.799 | 0.353 / 0.332 / 0.342 |
| median $\lvert\iota_Q - 90\rvert$: $f_{\rm ref}$ / $t = 0$ | 39.0 / 12.6 | 29.4 / 29.9 |

Reading: the inclination at $f_{\rm ref}$, which the LVK quotes, is far from edge-on; the
orbital axis precesses so that, at merger, most posterior samples are within $20^\circ$ of
edge-on. The prior does not produce this, so it comes from the data. The result rests on the
extrapolated surrogate (`r-t01-nrsur-extrapolation`) and is quoted at $t = 0$ because the
peak time is unstable (`r-t01-peak-ambiguity`). Whether "surprisingly" edge-on holds
depends on a comparison not yet made (for example, with the $\iota_Q(0)$ distribution of
other events or of posterior draws under a different spin prior).
