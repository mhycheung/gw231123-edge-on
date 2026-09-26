---
id: r-t01-nrsur-extrapolation
title: NRSur7dq4v2 is used outside its training range for GW231123
type: result
kind: assumption
status: done
depends_on: [t01-merger-inclination]
uses: [Ravishankar2026, Varma2019, GW231123PE2025]
artifacts: [tasks/t01-merger-inclination/S3/result_C00-NRSur7dq4_NRSur7dq4v2_2026-09-25.json]
code: [src/merger_inclination/waveform.py]
summary: 'Every inclination in this project comes from NRSur7dq4v2 (and NRSur7dq4 as a cross-check). The GW231123 maximum-likelihood spins, 0.96 and 0.99, lie outside the surrogate training range ($\chi \le 0.8$); the LVK parameter estimation used the same extrapolated model, so the posterior rests on the same assumption.'
verification: unverified
---

# NRSur7dq4v2 is used outside its training range for GW231123

The frames, modes and inclinations in t01 and t02 are computed with NRSur7dq4v2
[@Ravishankar2026], with NRSur7dq4 [@Varma2019] as a cross-check. Both are trained on
spins $\chi \le 0.8$. The maximum-likelihood sample of the GW231123 `C00:NRSur7dq4` posterior
[@GW231123PE2025] has spins 0.96 and 0.99 (MEASURED; `S3/result_*.json`), so the model is
extrapolated.

The posterior samples were drawn with the same extrapolated model, so the inclination is
computed consistently with the posterior. Whether the extrapolated coprecessing frame is
accurate near merger is not tested in this project.
