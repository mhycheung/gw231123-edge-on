---
status: done
---

# t02 S3 results (2026-09-25)

All numbers are MEASURED from `S3/summary_2026-09-25.json` and
`data/t02-posterior-inclination/{post,prior}_2026-09-25.npz`, produced by
`pixi run python tasks/t02-posterior-inclination/S3/aggregate.py`. Provenance: `S3/provenance.yaml`.

## Coverage

18185/18185 posterior and 5000/5000 prior samples evaluated, 0 failures (S2/run.md).

## Numbers (degrees; median [5 %, 95 %])

| quantity | posterior | prior |
|---|---|---|
| iota at f_ref | 59.2 [35.3, 137.5] | 90.9 [26.6, 154.6] |
| iota_Q(0) | 82.3 [60.7, 109.3] | 91.0 [26.8, 154.5] |
| iota_E(0) | 82.7 [59.3, 110.4] | 91.3 [26.3, 154.7] |
| P(\|iota - 90\| < 10): f_ref / iota_Q(0) / iota_E(0) | 0.001 / 0.332 / 0.283 | 0.182 / 0.168 / 0.173 |
| P(\|iota - 90\| < 20): f_ref / iota_Q(0) / iota_E(0) | 0.027 / 0.823 / 0.799 | 0.353 / 0.332 / 0.342 |
| median \|iota_Q - 90\|: f_ref / t = 0 | 39.0 / 12.6 | 29.4 / 29.9 |
| t_ref [M] | -217.7 [-239.5, -191.1] | -105.7 [-669.9, -31.5] |
| helicity flips of tracked iota_E | 0 % | 11.3 % |

The posterior median of |iota_Q - 90 deg| has its minimum, 8.2 deg, at t = -12 M.

## Figures

1. `bands_2026-09-25.{pdf,png}`: iota_Q (solid) and iota_E (dashed) against t/M. Posterior is
   C0 and prior is C1. The shading shows the pointwise 68 % and 90 % bands, and the lines are
   medians. The gray band and line mark the 90 % range and median of the posterior t_ref. The
   black bar at the left edge is the posterior iota at f_ref. **Caveat:** the posterior iota
   is bimodal about 90 deg (modes near 50 and 130 deg at f_ref, near 78 and 101 deg at t = 0),
   so the pointwise median lies between the modes and does not describe a typical sample.
2. `t0_hist_2026-09-25.{pdf,png}`: densities of iota_Q(0) (left) and iota_E(0) (right) for
   the posterior and the prior, with iota at f_ref in black (solid: posterior, dotted: prior).
   The dashed line marks 90 deg.
3. `folded_bands_2026-09-25.{pdf,png}` (supplementary, not in the plan): the pointwise median
   (thick line), the 68 % band (shaded, iota_Q only) and the 95th percentile (thin line) of
   |iota - 90 deg|, the angle from edge-on. This quantity is unimodal. Otherwise as in figure 1.

## Reading

- Control: under the isotropic prior, the distribution of iota does not change with time.
  The prior median |iota_Q - 90| is 29.4 deg at f_ref and 29.9 deg at t = 0, and the prior
  bands are flat in t. The calculation adds no preference for edge-on by itself.
- Posterior: both modes of iota move toward 90 deg between t_ref and merger. The median
  distance from edge-on falls from 39 deg to 12.6 deg at t = 0, and P(|iota_Q(0) - 90| < 20)
  is 0.82 against 0.33 for the prior. The data prefer this geometry; the prior does not
  produce it.
- iota_Q is constant for t > ~+20 M in every sample. The inferred reason, not tested: the
  coprecessing frame stops evolving after the ringdown. The post-merger part of the bands
  should not be interpreted until this is checked.
- In 11.3 % of prior samples, but in no posterior sample, the tracked iota_E switches to the
  positive-helicity maximum at some time. Where this happens, the prior iota_E band follows
  the other emission lobe.
- The t = -4300 M grid point is NaN in every sample: the first grid time falls before the
  waveform start. No other time is affected.
