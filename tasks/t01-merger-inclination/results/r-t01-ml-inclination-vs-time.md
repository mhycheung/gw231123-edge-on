---
id: r-t01-ml-inclination-vs-time
title: 'For the maximum-likelihood sample, $\iota_Q$ rises from 64 deg at $f_{\rm ref}$ to about 90 deg near merger'
type: result
kind: figure
status: done
depends_on: [r-t01-nrsur-extrapolation, r-t01-peak-ambiguity]
uses: [GW231123PE2025, Ravishankar2026]
artifacts:
  - tasks/t01-merger-inclination/S3/fig2_inclination_vs_time_2026-09-25.png
  - tasks/t01-merger-inclination/S3/result_C00-NRSur7dq4_NRSur7dq4v2_2026-09-25.json
  - tasks/t01-merger-inclination/S3/result_C00-NRSur7dq4_NRSur7dq4_2026-09-25.json
  - data/t01-merger-inclination/S3/result_C00-NRSur7dq4_NRSur7dq4v2_2026-09-25.series.npz
code: [src/merger_inclination/inclination.py, src/merger_inclination/frames.py, tasks/t01-merger-inclination/S3/plots.py]
summary: 'ML sample 6096 of C00:NRSur7dq4 ($\iota = 64.3^\circ$ at $f_{\rm ref} = 10$ Hz): $\iota_Q(t)$ reaches a maximum of $89.1^\circ$ (v2) / $90.0^\circ$ (v1) at $t \approx -6\,M$. At the strain peak $t^*$, $\iota_Q = 81.8^\circ$ (v2, $t^* = -27\,M$) or $89.8^\circ$ (v1, $t^* = -2.7\,M$).'
verification: unverified
evidence: tasks/t01-merger-inclination/S3/provenance.yaml
---

# For the maximum-likelihood sample, $\iota_Q$ rises to about $90^\circ$ near merger

![](../S3/fig2_inclination_vs_time_2026-09-25.png)

All numbers MEASURED; `S3/result_*.json`, `S3/provenance.yaml`.

| model | $t^*$ ($M$) | $\iota_Q(t^*)$ (deg) | $\iota_E(t^*)$ (deg) |
|---|---|---|---|
| NRSur7dq4v2 | $-27.0$ | 81.8 | 80.4 |
| NRSur7dq4 (v1) | $-2.7$ | 89.8 | 88.6 |

- $\iota$ at $f_{\rm ref} = 10$ Hz ($t_{\rm ref} = -196\,M$): $64.3^\circ$.
- Maximum of $\iota_Q(t < 20\,M)$: $89.1^\circ$ (v2), $90.0^\circ$ (v1), at $t \approx -6\,M$.
- $\iota_Q(-1000\,M) = 85^\circ$: $f_{\rm ref}$ sits near a minimum of $\iota_Q(t)$.

The two models differ at $t^*$ because they pick different peaks of $|h|$
(`r-t01-peak-ambiguity`), not because they disagree on $\iota_Q(t)$. This is one sample;
the posterior result is `r-t02-near-edge-on-at-merger`.
