---
status: done
---

# S1: metric code, controls, cost

Date: 2026-09-25. Code: `src/mismatch_metric/` (`defaults.py`, `metric.py`, `batch.py`),
tests `src/tests/test_metric.py` (8 passed: `pixi run pytest -q src/tests/test_metric.py`).
All numbers below are MEASURED with the command named beside them, run from the repo root.

## Outcome

The gate passes with two recorded deviations from the plan's wording. Both are explained below
and need the user's review; S2 proceeds on them (autonomy: autonomous).

| check | plan's bar | result | verdict |
|---|---|---|---|
| (a) optimal SNR, ML sample | 1 % | H1 $1.4\times10^{-8}$, L1 $1.9\times10^{-9}$ relative (with calibration) | pass |
| (b) $\iota_Q(0)$, ML sample, v1 | $10^{-6}$ deg | $6\times10^{-13}$ deg | pass |
| (c) quadratic mismatch at $10^{-3}$ | ≥ 90 % within 10 % | literal 63 %; symmetric $\pm\delta x$ 90.4 %; literal at $10^{-4}$ 92.6 % | deviation 1 |
| (c) control, unprojected metric | must miss more | 12 %, 12 %, 13 % | pass |
| (d) $\log\det g^\theta$, steps $h$ vs $h/2$ | 0.05 at 20 points | 18 of 20 within 0.05; the other two 0.13, 0.14 | deviation 2 |
| (e) face-on aligned | cond $(\phi_{\rm ref},\psi)$ block $>10^6$, $s$ finite | $1.3\times10^{16}$, $\log s=-20.37$ | pass |
| (f) one-sided differences | record | W 0.7 %, P 5.5 % of points (estimate from the stencil rule) | recorded |
| (g) cost | ≤ 60 CPU-h for W = 8000, P = 2001 | 2.7 s per point on a loaded node: 7.6 CPU-h | W = 8000, P = 2001 kept |

Extra control: the prior assumption of the score (isotropic Cartesian spins in the LAL frame
and an isotropic line of sight, independent). `check_prior.py 40000`: 40 000 draws from the PE
prior forms converted with `SimInspiralTransformPrecessingNewInitialConditions`; all ten KS and
correlation tests $p>0.06$ ($\cos\iota$: $p=0.86$). Control that must fail ($\theta_{JN}$ uniform
instead of sine): $\cos\iota$ $p=10^{-235}$, $N\cdot\hat\chi_1$ $p=1.6\times10^{-5}$. The 5000 stored
prior samples give $\cos\iota$ $p=0.014$ and $\cos t_1$ $p=0.028$; the tilt prior is sine by
construction, so these are fluctuations of 5000 draws. Files `check_prior_2026-09-25.json`,
`check_prior_fresh40000_2026-09-25.json`.

## (a) SNR check: calibration is needed

`pixi run python tasks/t03-mismatch-volume/S1/check_a.py`. Without calibration our SNRs differ
from the stored ones by +1.3 % (H1) and −0.7 % (L1); with bilby's cubic-spline calibration
(reimplemented in `metric.SplineCalibration` from bilby 2.6.0) they agree to $10^{-8}$. The metric
itself ignores calibration, as the plan states.

## The waveform used for derivatives (debugging rounds 1 and 2)

The first control run (`controls_2026-09-25_round0.json`) failed (d): 11 of 20 points within
0.05, worst 1.6. The derivative error doubled at each halving of the step along $M$, $\chi_{iz}$ and
sometimes $\phi_{\rm ref}$: the signature of a discontinuity. Scans of the unit waveform along one
coordinate (`check_taper.py`) located two sources, both in the PE's own waveform (bilby →
`SimInspiralFD`):

1. **End of the series.** LAL's NRSur7dq4 time series ends abruptly 100 $M$ after the peak at
   0.2 % of the peak amplitude, and gains one sample per 0.045 $M_\odot$ in $M$: a jump of
   $7.5\times10^{-4}$ (normalised), 43 % of its power above 300 Hz.
2. **Start taper.** NRSur7dq4 allows $f_{\min}=0$, so LAL uses its fallback conditioning
   (`LALSimInspiralGeneratorConditioning.c`, lalsuite 7.26): `ChooseTDWaveform` plus
   `TAPER_START`, a Planck taper from the first sample to the second extremum of each
   polarisation, a sample index. Its length is 100–185 $M$ (median 145 $M$) at the check points
   and jumps by one sample as the parameters move: jumps of $1.8\times10^{-4}$, mostly below 30 Hz.
   The epoch is exactly $-4300\,M$ (continuous).

These jumps have mismatch $\lesssim 3\times10^{-7}$, irrelevant to the likelihood at SNR 20, but they
dominate finite differences. Fix (`metric.polarizations`, `defaults.TAPERS_M`):
`SimInspiralChooseTDWaveform`, a Planck start taper over 145 $M$ from the start and a $\cos^2$
end taper from 60 $M$ to 95 $M$ after $t=0$, both in continuous time; then LAL's own padding and
FFT (`_td_to_fd`, tested equal to `SimInspiralFD` in `test_rebuilt_fd_equals_lal`). Results
(`check_taper_2026-09-25_round2.json`):
- mismatch between our waveform and the PE's at the 20 check points: max $3.5\times10^{-5}$,
  median $2.6\times10^{-6}$;
- jump scans along $M$, $\phi_{\rm ref}$, $\chi_{1z}$: 20, 17, 16 spikes before; 0, 0, 0 after.

This is a deviation from "the waveform is the likelihood's": ours differs from it by at most
$3.5\times10^{-5}$ in mismatch, i.e. $\rho^2\times3.5\times10^{-5}=0.015$ in $\ln L$ at $\rho=20.6$.

## Step choice (d)

Derivatives (`metric.metric_x`): a pilot second-order pass gives the projected diagonal
$g_{kk}$; the final step is $h_k=\delta/\sqrt{g_{kk}}$, capped at `STEP_MAX`, with a fourth-order
central stencil; one-sided second order where a stencil point would leave $q\le1$, $|\chi|\le0.99$.
The $\iota_Q(0)$ gradient uses fixed steps `K_STEPS`, second order.

`check_d_scan.py` scanned $\delta$ from 0.2 to 0.003 at the eight worst points: $\log\det g^\theta$
drifts at $\delta\ge0.05$ (truncation; e.g. win2 by 0.5) and becomes noisy below $\delta\approx0.003$.
It does not change at all with `K_STEPS` (×0.25 to ×4): $\det g^\theta$ depends on $\iota_Q(0)$ only through
$\partial\iota_Q(0)/\partial(\iota,\phi_{\rm ref})$, since changing $\partial\iota_Q(0)/\partial x_{\rm int}$ is a shear of the chart
(unit Jacobian; `test_logdet_independent_of_intrinsic_gradient`). Chosen: $\delta=0.0125$, caps
$M\le1\,M_\odot$, $q\le0.01$, spins $\le0.02$, angles $\le0.05$ rad.

**Deviation 2.** With these, 18 of 20 points agree to 0.05 between $h$ and $h/2$; post8 −0.14,
win2 +0.13; median $|{\rm diff}|$ 0.01 (`controls_2026-09-25_final.json`). An error of 0.14 in
$\log\det$ is 7 % in $s$, while $s$ spans a factor $\sim e^{10}$ across points, so it cannot move
$R_{\rm edge}$ at the level of its bootstrap error; S2 tests this directly by rerunning 400 W
points with steps halved (`win_fac0.5_0000.npz`) and S3 reports $R_{\rm edge}$ from both.

## Quadratic check (c): cubic terms

`check_c_scaling.py`: along the same 99 directions, the median relative error of the metric
prediction is 7.8 % at mismatch $10^{-3}$, 3.0 % at $10^{-4}$ and 1.1 % at $10^{-5}$: it falls by
$\approx\sqrt{10}$ per decade, as cubic terms do; an error in the metric would not scale. Averaging
the mismatch at $+\delta x$ and $-\delta x$ cancels odd orders: 93 % within 10 % at $10^{-3}$.

**Deviation 1.** The plan's literal test at $10^{-3}$ fails (63 %) because the mismatch
function is not quadratic at that scale, not because the metric is wrong. The gate is taken
as the symmetric test at $10^{-3}$ (90.4 %, 66 of 73; the others had $+\delta x$ or $-\delta x$ outside the
domain) and the literal test at $10^{-4}$ (92.6 %), each with its unprojected control failing
(12 %, 13 %). Meaning for the result: at SNR 20.6, where the relevant mismatches are
$\sim10^{-3}$, the local metric describes single directions to $\pm20$ % (5–95 %); cubic terms are
odd and do not change the volume at leading order.

## Files

| file | what |
|---|---|
| `check_a.py` | (a) |
| `check_prior.py`, `check_prior_*.json` | prior-isotropy control |
| `check_taper.py`, `check_taper_2026-09-25.json` (end taper only), `..._round2.json` (final tapers) | jump scans, taper mismatch |
| `check_c_scaling.py`, `check_c_scaling_2026-09-25.json` | (c) scaling |
| `check_d_scan.py`, `check_d_scan_2026-09-25.json` | (d) step scan (run with $\delta$-caps before the final caps) |
| `controls.py`, `controls_2026-09-25_final.json` | (c)–(g), final settings |
| `controls_2026-09-25_round{0,1,2,3}.json` | earlier runs: round0 original steps and LAL waveform; round1 end taper, adaptive steps $\delta=0.05$; round2 both tapers; round3 $\delta=0.0125$ (the (c) section of round0–3 has only the literal test) |
