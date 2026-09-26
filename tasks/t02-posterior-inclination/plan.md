---
id: t02-posterior-inclination
title: Inclination vs time over the GW231123 NRSur posterior and prior
short_name: posterior-incl
type: task
status: done
depends_on:
- t01-merger-inclination
privacy: public
summary: 'Plan: iota_Q(t) and iota_E(t) with NRSur7dq4v2 for every sample of the GW231123 C00:NRSur7dq4 posterior and 5000 prior draws; credible bands vs t/M and the distributions at t = 0.'
verification: unverified
autonomy: autonomous
hold_at: []
---

# Inclination vs time over the GW231123 NRSur posterior and prior: credible bands and t = 0 distributions

<!-- opsci:node-table: generated from the front matter by `opsci map build`; edit the front matter, not this table -->

| task | `t02-posterior-inclination` |
|---|---|
| **short name** | `posterior-incl` |
| **status** | done |
| **privacy** | public |
| **verification** | unverified |
| **autonomy** | autonomous |
| **depends on** | `t01-merger-inclination` |
| **summary** | Plan: iota_Q(t) and iota_E(t) with NRSur7dq4v2 for every sample of the GW231123 C00:NRSur7dq4 posterior and 5000 prior draws; credible bands vs t/M and the distributions at t = 0. |

<!-- /opsci:node-table -->

## Goal

For every sample of the GW231123 `C00:NRSur7dq4` posterior (18185) and for the 5000 stored
prior samples, compute with NRSur7dq4v2 the inclination by the coprecessing axis, iota_Q(t),
and by the direction of maximum emission, iota_E(t), using the t01 code. Deliver (1) pointwise
credible bands (median, 68 %, 90 %) of iota_Q and iota_E against t/M, posterior and prior
overlaid, and (2) the distributions of iota_Q and iota_E at t = 0, posterior and prior, with
summary numbers. Done when: the S1 gate passes, at least 99 % of posterior and prior samples
are evaluated, the S3 plots and numbers are sent to the owner on Slack.

## Design

**Per sample** (function `sample_inclination` in `src/merger_inclination/batch.py`):
evaluate NRSur7dq4v2 as in t01 (dt = 0.1 M, f_low = 0, f_ref read from the file = 10 Hz,
line of sight N = n(iota, pi/2 - phase)). t = 0 is the surrogate's time origin (the peak of
the total amplitude; the owner's "t = 0"). Store:
- iota_Q(t) on the common grid T_Q = -4300 ... +100 M, step 1 M (float32);
- iota_E(t) on T_E = [-1000, -980, ..., -200] ∪ [-195, -190, ..., +50] M (91 times): the full
  sphere search with helicity orientation of t01 (`emission_maxima`) at t = 0, then tracked
  backward and forward from t = 0 by local Nelder-Mead (`track_emission`); plus the helicity
  of the tracked axis at each time (a sign change flags a jump to the other maximum);
- iota_Q(0), iota_E(0), t_ref, iota_Q(t_ref), the input iota, a failure flag and message.
The same function runs on the prior samples (`C00:NRSur7dq4/priors/samples`, which carry the
Cartesian spins, iota, phase and masses).

**Why the prior.** The PE prior is isotropic in spin directions and in the orientation of J.
Precession moves iota between f_ref and t = 0; comparing the posterior with the same
calculation on prior draws separates what the data demand from what the geometry does to any
draw. The prior masses (M from 158 to 679 Msun, q up to 6.0; MEASURED) are all inside what the
surrogate evaluates (q <= 6 with extrapolation warning).

**Bands.** Pointwise equal-tailed quantiles (5, 16, 50, 84, 95 %) over samples at each time,
equal weights (the posterior samples are unweighted draws). The t_ref of each sample differs
(t_ref depends on M); the plot marks the median and 90 % range of t_ref.

**Numbers at t = 0.** Median and 90 % interval of iota_Q(0), iota_E(0) and of the input iota
(at f_ref); P(|iota - 90 deg| < 10 deg) and P(|iota - 90 deg| < 20 deg) for each, posterior and
prior.

**Rejected alternatives.**
- iota_E by a full-sphere search at every time: 0.24 s per time, 91 times, 23185 samples =
  140 CPU-h; local tracking from t = 0 costs ~0.05 s per time (t01 series).
- A subset of posterior samples: the full set costs ~25 CPU-h, affordable as a job array.
- Time axis in seconds: M differs per sample; t/M is the common axis (owner's choice).
- iota at t*: t* is unstable for these signals (t01: three near-equal peaks); the owner fixed t = 0.

## Constraints

- Conventions as in t01 (`src/merger_inclination/__init__.py`): LAL source frame at f_ref,
  N = n(iota, pi/2 - phase), h = h+ - i hx, geometric units with the detector-frame total mass,
  angles in radians internally and degrees in plots. t01's convention gate holds for this code.
- Environment: the pixi project at the repo root; data from `tasks/t01-merger-inclination/S1/setup_data.sh`.
- Compute (owner, 2026-09-25): the full run is a SLURM job array, one single-CPU array task
  per chunk, submitted with the account and partition from `config/site.local.yaml` (R06); it
  does not run inside the main agent's own allocation. Only the S1 test chunks run in the main
  agent's allocation.
- Outputs: per-chunk arrays in `data/t02-posterior-inclination/chunks/{post,prior}_<NNNN>.npz`,
  chunk size set in S1 so that one chunk takes ~15 min on one CPU; aggregated arrays in `data/t02-posterior-inclination/`; small outputs in
  `tasks/t02-posterior-inclination/<S>/`. All data listed in `data/MANIFEST.yaml`.
- Rules: R01, R02, R04, R05, R06, R07 (reuse t01's code and data; do not re-download).
- Shared code: add `batch.py` to `src/merger_inclination/`; no other task runs, so work on `main`.
- Plots: `publication-plots` conventions; posterior C0, prior C1, iota_Q solid, iota_E dashed,
  the f_ref iota black. Slack via the `slack` skill.

## Delegation

None. The work is one sequential track; the long run is a SLURM job array watched by the
main agent.

## Subtask S1: batch code and test run — main agent — ~45 min (±2×)

- Output directory: tasks/t02-posterior-inclination/S1/
- Delivers: `src/merger_inclination/batch.py` (per-sample function; chunk runner
  `python -m merger_inclination.batch --set post|prior --chunk k --size n --out DIR`, which skips
  a chunk whose output exists); an array script `tasks/t02-posterior-inclination/S2/array.sh`
  that maps SLURM_ARRAY_TASK_ID to (set, chunk) and reads nothing site-specific (account and
  partition are given at submission from `config/site.local.yaml`); a pytest in `src/tests/test_batch.py`; `S1/test_run.md`.
- Steps: run 100 posterior samples (0-99, plus 6096) and 100 prior samples (0-99) in the main
  agent's allocation, output to `data/t02-posterior-inclination/test/` (not reused by S2).
- Gate (the full run is ~25-35 CPU-h): (a) the ML sample (index 6096) gives iota_Q(0) =
  88.715 deg, the t01 value (`tasks/t01-merger-inclination/S3/peak_candidates_2026-09-25.json`,
  `iota_Q_at_t0_deg` = 88.71503841002698), to 1e-6 deg; (b) |iota_Q(t_ref) - iota| < 1e-3 rad for
  every sample of both test chunks; (c) failures < 1 %; (d) for the ML sample and 20 random
  test samples, the tracked iota_E at t = -100 M and t = -1000 M equals a fresh full-sphere
  `emission_maxima` at that time to 0.1 deg in at least 95 % of cases (the tracker stays on the
  global, negative-helicity maximum); (e) the
  measured cost per sample is recorded and sets the chunk size (~15 min per chunk). Control that must
  fail: (a) with N built from (iota, phase) must differ from 88.715 deg by > 1 deg.
- Fatal if: the gate cannot pass after two debugging rounds; the predicted cost > 80 CPU-h.

## Subtask S2: full run as a SLURM job array — main agent — ~1 h wall (±2×), ~35 CPU-h

- Output directory: data/t02-posterior-inclination/chunks/ (all posterior and prior chunks);
  SLURM logs in data/t02-posterior-inclination/slurm/.
- Delivers: all chunks, and `S2/run.md` with the submit command, job id, start/end times,
  failures and resubmissions.
- Steps: submit one array covering every chunk (`sbatch --array=0-<n-1> -A <account>
  -p <partition> -n 1 -c 1 --mem 2G -t <3x the S1 chunk time>`), with account and partition
  from `config/site.local.yaml`; record the job id and the check command
  (`ls data/t02-posterior-inclination/chunks | wc -l`, `squeue -j <id>`) in the task context;
  start `wait_slurm.sh <id>` as a background waker and do a wait jump. Resubmit the missing
  chunks once if array tasks fail (time limit, node failure).
- Fatal if: failures > 1 % of either set with a common cause that is not a surrogate range refusal.

## Subtask S3: aggregate, plots, report — main agent — ~45 min (±2×)

- Output directory: tasks/t02-posterior-inclination/S3/
- Delivers: `data/t02-posterior-inclination/{post,prior}_2026-MM-DD.npz` (concatenated arrays
  with sample indices); `S3/summary_2026-MM-DD.json` (quantiles at t = 0, the probabilities
  above, failure counts, helicity-flip fraction of the tracked iota_E); `S3/provenance.yaml`;
  PDFs + PNGs:
  1. band plot: iota_Q and iota_E vs t/M, posterior and prior, 68 % and 90 % shaded, median
     lines; left panel -4300 to +100 M, right panel -250 to +50 M; median and 90 % range of t_ref
     marked; the posterior iota at f_ref shown as a band on the left edge;
  2. distributions at t = 0: histograms (densities) of iota_Q(0) and iota_E(0), posterior and
     prior, with the posterior and prior iota at f_ref for reference; x from 0 to 180 deg, 90 deg
     marked.
- Steps: aggregate, compute numbers, plot, send the PNGs, captions and a result summary to
  Slack.

## Escalate only if fatal

- The prior samples lack Cartesian spins or cannot be evaluated by the surrogate (> 1 %
  refusals): drop the prior comparison, report, and continue with the posterior only.
- Array tasks keep failing after one resubmission for a cause outside the code (queue,
  quota): record the chunk count and stop.

## Budget

S1 45 min, S2 ~1 h wall (35 CPU-h, queue wait extra), S3 45 min. Ceiling: 80 CPU-h, 2 GB of
data.
