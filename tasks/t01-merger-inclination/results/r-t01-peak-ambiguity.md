---
id: r-t01-peak-ambiguity
title: 'The time of peak strain $t^*$ is unstable for GW231123: $|h|$ has three near-equal peaks'
type: result
kind: statement
status: done
depends_on: [r-t01-nrsur-extrapolation]
artifacts:
  - tasks/t01-merger-inclination/S3/fig1_strain_amplitude_2026-09-25.png
  - tasks/t01-merger-inclination/S3/peak_candidates_2026-09-25.json
code: [tasks/t01-merger-inclination/S3/peak_candidates.py]
summary: 'For the ML sample, $|h_+ - i h_\times|$ along the line of sight has three peaks within 1-9 % of each other, at $t = -27, -13, -3\,M$. NRSur7dq4v2 and NRSur7dq4 agree on $\iota_Q$ at each peak (82, 87-88, 89-90 deg) but choose different peaks as highest (margins 1-2 %). An inclination "at peak strain" is therefore ill-defined; t02 reports $\iota$ at $t = 0$ of the model time axis instead.'
verification: unverified
evidence: tasks/t01-merger-inclination/S3/provenance.yaml
---

# The time of peak strain is unstable for GW231123

![](../S3/fig1_strain_amplitude_2026-09-25.png)

MEASURED (`S3/peak_candidates_2026-09-25.json`): the observed-strain amplitude of the ML
sample has three peaks within 1-9 % of each other, at $t = -27$, $-13$ and $-3\,M$. The two
surrogate versions agree on $\iota_Q$ at each peak ($82^\circ$, $87$-$88^\circ$,
$89$-$90^\circ$) but differ on which peak is highest, by margins of 1-2 %.

Consequence: a single "inclination at peak strain" depends on which peak wins, which is
decided by percent-level model differences. Results should be quoted as a function of time
or at a fixed time such as $t = 0$.
