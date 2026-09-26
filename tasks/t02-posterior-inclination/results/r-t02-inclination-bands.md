---
id: r-t02-inclination-bands
title: 'Credible bands of $\iota_Q(t)$ and $\iota_E(t)$ over the GW231123 posterior and prior'
type: result
kind: figure
status: done
depends_on: [r-t01-nrsur-extrapolation, r-t01-beaming-offset, r-t01-peak-ambiguity]
uses: [GW231123PE2025, Ravishankar2026]
artifacts:
  - tasks/t02-posterior-inclination/S3/bands_2026-09-25.png
  - tasks/t02-posterior-inclination/S3/folded_bands_2026-09-25.png
  - data/t02-posterior-inclination/post_2026-09-25.npz
  - data/t02-posterior-inclination/prior_2026-09-25.npz
code: [src/merger_inclination/batch.py, tasks/t02-posterior-inclination/S3/aggregate.py]
summary: 'Pointwise 68 % and 90 % bands of $\iota_Q(t)$, $\iota_E(t)$ against $t/M$ for all 18185 posterior samples and 5000 prior draws. The prior bands are flat in $t$ (control). The posterior $\iota$ is bimodal about $90^\circ$, so the band median of $\iota$ is misleading; the folded $|\iota - 90^\circ|$ plot is unimodal. $\iota_Q$ is constant for $t > +20\,M$ in every sample (cause not tested): do not read the post-merger part.'
verification: unverified
evidence: tasks/t02-posterior-inclination/S3/provenance.yaml
---

# Credible bands of $\iota_Q(t)$ and $\iota_E(t)$

![](../S3/folded_bands_2026-09-25.png)

![](../S3/bands_2026-09-25.png)

Details and reading: `S3/results.md`. All numbers MEASURED from
`S3/summary_2026-09-25.json` (`S3/provenance.yaml`).

- Coverage: 18185/18185 posterior and 5000/5000 prior samples, 0 failures.
- Control: the prior median $|\iota_Q - 90^\circ|$ is $29.4^\circ$ at $f_{\rm ref}$ and
  $29.9^\circ$ at $t = 0$; the calculation adds no preference for edge-on by itself.
- The posterior $\iota$ is bimodal about $90^\circ$ (modes near $50^\circ$ and $130^\circ$ at
  $f_{\rm ref}$, near $78^\circ$ and $101^\circ$ at $t = 0$). The pointwise median of $\iota$
  lies between the modes; $|\iota - 90^\circ|$ (top figure) is unimodal.
- Limits: $\iota_Q$ is constant for $t > +20\,M$ in every sample (inferred, not tested: the
  coprecessing frame stops evolving after the ringdown). In 11.3 % of prior samples, and no
  posterior sample, the tracked $\iota_E$ switches emission lobe.
