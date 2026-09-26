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
summary: 'Plan: mismatch metric of NRSur7dq4 over the intrinsic parameters and the inclination at merger, with the extrinsic nuisances profiled; its volume per unit prior probability compared between edge-on and non-edge-on regions near GW231123.'
verification: unverified
autonomy: autonomous
hold_at: []
---

# Density of distinguishable waveforms vs inclination at merger: metric volume per unit prior probability against $\iota_Q(0)$

<!-- opsci:node-table: generated from the front matter by `opsci map build`; edit the front matter, not this table -->

| task | `t03-mismatch-volume` |
|---|---|
| **short name** | `mismatch-vol` |
| **status** | done |
| **privacy** | public |
| **verification** | unverified |
| **autonomy** | autonomous |
| **depends on** | `t02-posterior-inclination`, `t01-merger-inclination` |
| **summary** | Plan: mismatch metric of NRSur7dq4 over the intrinsic parameters and the inclination at merger, with the extrinsic nuisances profiled; its volume per unit prior probability compared between edge-on and non-edge-on regions near GW231123. |

<!-- /opsci:node-table -->

## Goal

Test one necessary condition of the hypothesis that GW231123 is inferred edge-on at merger because edge-on,
high-mass, strongly precessing NRSur7dq4 waveforms are flexible enough to absorb noise artefacts or model
error. Measure the density of distinguishable waveforms per unit prior probability, $s(\theta)$ below, as a function of the
inclination at merger $\iota_Q(0)$ and of $\chi_p$, in the GW231123 mass window and over the posterior. Deliver the ratio
$$ R_{\rm edge}=\frac{\langle s\rangle_{|\iota_Q(0)-90^\circ|<20^\circ}}{\langle s\rangle_{|\iota_Q(0)-90^\circ|\ge 20^\circ}} $$
with a bootstrap 68 % interval, for each $\chi_p$ bin. Done when the S1 gate passes, at least 99 % of points are
evaluated, and the S3 figures, numbers and a result file exist and are posted to the Notion Feed.
Reading: $R_{\rm edge}>1$ significantly, rising with $\chi_p$, supports the flexibility premise;
$R_{\rm edge}\le1$ within errors refutes it for this measure. $R_{\rm edge}>1$ is necessary, not sufficient (Design, "Limits").

## Design

**Origin.** The hypothesis is stated, untested, in App. C of arXiv:2607.21834. A literature search (2026-09-25)
found no computation of a mismatch-metric volume against inclination and precession. arXiv:1904.01683 builds
Euclidean mismatch coordinates only for (2,2), aligned-spin waveforms of fixed amplitude, so it does not apply here.

**Coordinates for derivatives.** $x=(M,q,\chi_{1x},\chi_{1y},\chi_{1z},\chi_{2x},\chi_{2y},\chi_{2z},\iota,\phi_{\rm ref},\psi,t_c)$: detector-frame total mass, $q=m_2/m_1\le1$
(bilby convention), Cartesian spins in the LAL $L$–$n$ frame at $f_{\rm ref}=10$ Hz, the LAL $\iota$ and $\phi_{\rm ref}$ at $f_{\rm ref}$,
polarization, coalescence time. Sky position (the PE's `azimuth`, `zenith` in the L1H1 frame) and the reference time are fixed at the ML sample
(index 6096 of `C00:NRSur7dq4`); $t_c$ is a shift about it. Distance is profiled by normalisation.

**Inner product and metric.** $\langle a,b\rangle=4\,\mathrm{Re}\sum_{D\in\{H1,L1\}}\int_{20\,\rm Hz}^{448\,\rm Hz}\tilde a_D\tilde b_D^*/S_D\,df$, with the PE's PSDs
(`C00:NRSur7dq4/psds`) and the PE's settings (8 s, 1024 Hz, `LALCBCWaveformGenerator`, NRSur7dq4, all modes), so that the
waveform is the likelihood's. With $\hat h=h/\sqrt{\langle h,h\rangle}$,
$$ g^{x}_{ij}=\langle\partial_i\hat h,\partial_j\hat h\rangle=\frac{\langle\partial_ih,\partial_jh\rangle-\langle h,\partial_ih\rangle\langle h,\partial_jh\rangle/\langle h,h\rangle}{\langle h,h\rangle}, $$
so that the Fisher matrix with distance profiled is $\rho^2g^x$. Derivatives: central finite differences for the first 10
coordinates; $\partial_{t_c}$ and $\partial_\psi$ analytically ($\tilde h\to-2\pi i f\,\tilde h$; rotation of $F_{+,\times}$).

**Inclination at merger and the profiled metric.** Kept coordinates $\theta=(M,q,\vec\chi_1,\vec\chi_2,\iota_Q(0))$, nuisances $\nu=(\phi_{\rm ref},\psi,t_c)$. $\iota_Q(0)$ is the
angle between the coprecessing $z$-axis and the line of sight at the surrogate's $t=0$ (peak of the total mode amplitude), computed with the
t01/t02 code (`merger_inclination`). Chart $y=(\theta,\nu)$, i.e. $\iota$ replaced by $\iota_Q(0)$; $K=\partial y/\partial x$ is the identity except the $\iota_Q(0)$ row,
obtained by finite differences through the same code. $g^y=K^{-\top}g^xK^{-1}$, and the profiled metric is the Schur complement
$$ g^\theta=A-B\,C^{+}B^\top,\qquad g^y=\begin{pmatrix}A&B\\B^\top&C\end{pmatrix}, $$
with $C^+$ the pseudo-inverse (relative cutoff $10^{-10}$; $C$ is singular where $\phi_{\rm ref}$ and $\psi$ are degenerate, e.g. face-on and aligned).
Only the inclination is taken at merger: the intrinsic state at $f_{\rm ref}$ and at merger are related one-to-one by the dynamics, so the
level sets of $\theta$, hence $g^\theta$ and the score below, do not depend on the time at which the intrinsic parameters are labelled.

**Score.** Under the PE prior the source orientation is isotropic and independent of the intrinsic state, so the orientation relative
to the merger frame is too (Haar measure is invariant under the fixed rotation from the $f_{\rm ref}$ frame to the merger frame; t02 observed
the prior $\iota_Q$ distribution to be time-independent). Hence $\pi_\theta(\theta)=\pi_{\rm int}(x_{\rm int})\,\tfrac12\sin\iota_Q(0)$, with $\pi_{\rm int}$ the PE prior density on
$(M,q,\vec\chi_1,\vec\chi_2)$ (mass part from the stored bilby prior with the Jacobian to $(M,q)$; spin part $1/(4\pi a^2 a_{\max})$ per spin). Score
$$ s=\frac{\sqrt{\det g^\theta}}{\pi_\theta(\theta)} . $$
Averaged over prior draws in a region $\mathcal R$, $\langle s\rangle_{\mathcal R}=\int_{\mathcal R}\sqrt{\det g^\theta}\,d\theta\,/\,\Pi(\mathcal R)$: metric volume ("number of distinguishable
waveforms") per unit prior probability. It is invariant under reparametrisation of $\theta$.
Secondary: $N_\rho=\sqrt{\det(I+\rho^2Dg^\theta D)}$ with $\rho=20.6$ (median network matched-filter SNR, MEASURED from the PE file) and $D$ the diagonal
of the prior standard deviations of $\theta$ in the window (counts only directions resolved at the event's SNR); and the number of
nuisance directions with eigenvalue of $\rho^2 D_\nu C D_\nu>1$ (the extra $\phi,\psi$ freedom that profiling hides).

**Point sets.** W (window): draws from the PE prior with $M\in[287.0,333.2]\,M_\odot$ and $q\in[0.685,0.974]$ (posterior 5–95 %, MEASURED), all spins and
orientations from the prior; target 8000. P (posterior): 2000 random posterior samples (seed 1) plus index 6096. Bins: six equal-prior bins in
$|\cos\iota_Q(0)|$; $\chi_p$ (at $f_{\rm ref}$) in $[0,0.4)$, $[0.4,0.7)$, $[0.7,1]$. Means with bootstrap (1000 resamples); medians alongside, since $s$ may be heavy-tailed.

**Limits.** By the Laplace approximation, posterior mass in a region that fits the data equally well scales as $\pi/\sqrt{\det g}$: a large metric
volume raises the best fit a region can reach on noise or model error, but lowers its posterior mass per unit fit. So $R_{\rm edge}>1$ is
necessary, not sufficient, for the flexibility explanation; the residual-absorption test (how much of a given residual an edge-on
region absorbs) is the complementary step and is not in this task. The metric is local: distant parameter regions that give similar
waveforms are not merged. Calibration uncertainty is ignored.

**Rejected alternatives.**
- Geometric placement coordinates of arXiv:1904.01683: (2,2) aligned-spin fixed-amplitude only.
- Full 12-dimensional volume with $\phi_{\rm ref},\psi$ kept: user chose intrinsic plus $\iota_Q(0)$ for the first version; the nuisance count is reported instead.
- JAX autodiff (JAXNRSur, arXiv:2607.24960 emulator): dynamics exposure and v1 match unverified; emulator gradients may be less accurate than its values. Finite differences with the PE's own waveform first.
- Stochastic template-bank count in 9 dimensions: far more waveform calls; the local metric volume answers the same question for small regions.
- $\iota$ at the peak of $|h|$: unstable for GW231123 (three near-equal peaks, t01); $t=0$ of the surrogate is smooth.

## Constraints

- Model: NRSur7dq4 (v1, the PE's model) for the waveform and for $\iota_Q(0)$; t02's $\iota_Q(0)$ values used NRSur7dq4v2, so the posterior-set $\iota_Q(0)$ is
  recomputed with v1 and the v1–v2 difference is reported for set P.
- Conventions as in t01 (`src/merger_inclination/__init__.py`): LAL source frame at $f_{\rm ref}$, angles in radians internally, degrees in plots (R01).
- Environment: the pixi project at the repo root; PE file and surrogate data from t01 (`data/t01-merger-inclination/`), not re-downloaded (R07).
- Compute: S1 runs in the main agent's allocation; S2 is a SLURM job array, one CPU per chunk, account and partition from
  `config/site.local.yaml` (R06). Chunk size set in S1 for ~15 min per chunk.
- Constants (window, $\rho$, bins, step sizes, cutoffs) declared once in `src/mismatch_metric/defaults.py` with their source (R04).
- Outputs: `data/t03-mismatch-volume/chunks/{win,post}_<NNNN>.npz` (per point: $x$, $g^x$, the $\iota_Q(0)$ row of $K$, $g^\theta$, $\log\det g^\theta$, $\log\pi_\theta$, $\log s$,
  $N_\rho$, nuisance count, $\iota_Q(0)$, $\chi_p$, flags); aggregates in `data/t03-mismatch-volume/`; listed in `data/MANIFEST.yaml`. Small outputs in `tasks/t03-mismatch-volume/<S>/` (R05).
- Shared code: new package `src/mismatch_metric/`; reuse `merger_inclination` without changing it. No other task runs; work on the current branch.
- Plots: `publication-plots` conventions, each with a `.caption.md` (AGENTS.md §2). Rules: R01, R02, R04, R05, R06, R07.

## Delegation

None. S1 is sequential code and debugging; S2 is a job array watched by the main agent.

## Subtask S1: metric code, controls, cost — main agent — ~3 h (±2×)

- Output directory: tasks/t03-mismatch-volume/S1/
- Delivers: `src/mismatch_metric/` (`defaults.py`, `metric.py` with waveform, inner product, $g^x$, $K$, $g^\theta$, $\pi_\theta$, $s$; `batch.py` chunk runner
  `python -m mismatch_metric.batch --set win|post --chunk k --size n --out DIR`, skipping existing outputs; window draws generated once with seed 1
  and saved to `data/t03-mismatch-volume/win_points.npz`); `tasks/t03-mismatch-volume/S2/array.sh`; `src/tests/test_metric.py`; `S1/controls.md`.
- Steps and gate (the full run is tens of CPU-h):
  (a) ML sample: optimal SNR per detector from our waveform and PSDs equals the stored `H1_optimal_snr`, `L1_optimal_snr` of index 6096 to 1 %;
  (b) ML sample: $\iota_Q(0)$ with v1 equals `iota_Q_at_t0_deg` for `NRSur7dq4` in `tasks/t01-merger-inclination/S3/peak_candidates_2026-09-25.json` to $10^{-6}$ deg;
  (c) quadratic check at 20 points (10 from P, 10 from W), 5 random directions each in the first 10 coordinates, step scaled to a
      predicted mismatch of $10^{-3}$: the direct $1-\max_{t_c}\langle\hat h_1,\hat h_2\rangle$ equals $\tfrac12\delta x^\top g^x_{/t_c}\,\delta x$ (metric with $t_c$ profiled) to 10 % in ≥ 90 % of cases.
      Control that must fail: the same test with the unprojected metric $\langle\partial_ih,\partial_jh\rangle/\langle h,h\rangle$ misses the 10 % bar in more cases;
  (d) step convergence: $\log\det g^\theta$ from steps $h$ and $h/2$ agree to 0.05 at the same 20 points; steps chosen here and fixed in `defaults.py`;
  (e) face-on aligned control ($M=300\,M_\odot$, $q=0.8$, $\chi_{1z}=\chi_{2z}=0.5$, in-plane spins 0, $\iota=0$): condition number of the $(\phi_{\rm ref},\psi)$ block of $C$ $>10^6$ and $s$ finite;
  (f) spins within one step of $|\chi|=0.99$ use one-sided differences; the fraction of such points is recorded;
  (g) measured cost per point sets the chunk size and the set sizes: W = 8000 and P = 2001 if the predicted total is ≤ 60 CPU-h, else W reduced to fit.
- Fatal if: (a), (b) or (c) cannot pass after two debugging rounds; predicted cost > 80 CPU-h even with W = 3000.

## Subtask S2: full run as a SLURM job array — main agent — ~2 h wall (±2×), ~40 CPU-h

- Output directory: data/t03-mismatch-volume/chunks/; SLURM logs in data/t03-mismatch-volume/slurm/.
- Delivers: all chunks; `S2/run.md` with the submit command, job id, times, failures and resubmissions.
- Steps: submit one array over all chunks (`sbatch --array=0-<n-1> -A <account> -p <partition> -n 1 -c 1 --mem 2G -t <3x the S1 chunk time>`), with
  account and partition from `config/site.local.yaml`; record the job id and the check command in the task context; post a `status` to the Feed;
  wait with a background waker and a wait jump; resubmit missing chunks once.
- Fatal if: failures > 1 % of either set with a common cause that is not a surrogate range refusal.

## Subtask S3: aggregate, figures, result — main agent — ~1.5 h (±2×)

- Output directory: tasks/t03-mismatch-volume/S3/
- Delivers: `data/t03-mismatch-volume/{win,post}_<date>.npz`; `S3/summary_<date>.json` ($R_{\rm edge}$ per $\chi_p$ bin with 68 % intervals, binned means and medians of $s$
  and $N_\rho$, nuisance counts, failure counts, v1–v2 $\iota_Q(0)$ differences for P); `S3/provenance.yaml`; figures (PDF + PNG, with captions):
  1. $\langle s\rangle$ and median $s$ against $|\cos\iota_Q(0)|$ for set W, one curve per $\chi_p$ bin, bootstrap 68 % bands, log $y$;
  2. the same for set P, with the P histogram of $\iota_Q(0)$ beneath;
  3. $N_\rho$ and the nuisance count against $|\cos\iota_Q(0)|$ for W.
  A result file `results/r-t03-edge-on-metric-volume.md` stating $R_{\rm edge}$ and its reading, with the Limits paragraph; `S3/results.md`.
- Steps: aggregate, compute, plot; post the result to the Notion Feed with figure 1 and `--mention`.

## Escalate only if fatal

- The stored bilby prior cannot be rebuilt to evaluate $\pi_{\rm int}$: use the analytic forms named in `C00:NRSur7dq4/priors/analytic` if they suffice; otherwise stop and report.
- $g^\theta$ is numerically singular (condition number $>10^{12}$) at more than 5 % of W: the finite-difference metric is too noisy for a 9-dimensional determinant; stop and report with the eigenvalue spectra.
- The quadratic check fails systematically (not at isolated points): the local metric does not describe the mismatch at the $10^{-3}$ scale; stop and report.

## Budget

S1 ~3 h, S2 ~2 h wall (~40 CPU-h, queue wait extra), S3 ~1.5 h. Ceiling: 80 CPU-h, 5 GB of data.
