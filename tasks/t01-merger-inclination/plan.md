---
id: t01-merger-inclination
title: Orbital inclination at peak strain from NRSur7dq4v2
short_name: merger-incl
type: task
status: done
privacy: public
summary: 'Plan: code that computes the orbital inclination at the peak of the observed strain with NRSur7dq4v2, by the coprecessing-frame axis and by the direction of maximum emission, applied to the GW231123 NRSur maximum-likelihood sample.'
verification: unverified
autonomy: autonomous
hold_at: []
---

# Orbital inclination at peak strain from NRSur7dq4v2: code and GW231123 result

<!-- opsci:node-table: generated from the front matter by `opsci map build`; edit the front matter, not this table -->

| task | `t01-merger-inclination` |
|---|---|
| **short name** | `merger-incl` |
| **status** | done |
| **privacy** | public |
| **verification** | unverified |
| **autonomy** | autonomous |
| **summary** | Plan: code that computes the orbital inclination at the peak of the observed strain with NRSur7dq4v2, by the coprecessing-frame axis and by the direction of maximum emission, applied to the GW231123 NRSur maximum-likelihood sample. |

<!-- /opsci:node-table -->

## Goal

Build a tested, reusable code in `src/merger_inclination/` that takes the intrinsic and
extrinsic parameters of a BBH (spins and inclination defined at a reference frequency
`f_ref`) and returns the orbital inclination at the time t* of peak observed strain
|h(t)|, h = h_+ - i h_x, in two ways with NRSur7dq4v2:
(1) iota_Q = angle between the line of sight N and the coprecessing-frame axis z_copr(t*)
from the surrogate quaternions; (2) iota_E = angle between N and the direction of maximum
emission at t*, from the full mode sum (all ell <= 5 modes).
Done when: the convention gate (S2) passes, the controls (S2) pass, both angles and t* are
computed for the maximum-likelihood sample of the GW231123 NRSur7dq4 posterior, and the
plots of S3 are sent to the owner on Slack.

## Design

**Inputs.** From a PESummary file: `mass_1`, `mass_2` (detector frame), `spin_1x..z`,
`spin_2x..z`, `iota`, `phase`, `luminosity_distance`; `f_ref` and the approximant are read
from the analysis metadata/config of the same label, never hard-coded (R04). These are the
LAL source-frame quantities at `f_ref`: z along the orbital angular momentum, x from the
lighter to the heavier BH. The line of sight in that frame is
N = (sin iota cos(pi/2 - phase), sin iota sin(pi/2 - phase), cos iota), the LALSimulation
convention for NRSur7dq4 (angles (iota, pi/2 - phiRef)). Only iota and phase matter;
psi, sky position, time and distance do not change |h| up to a constant scale.

**Surrogate.** gwsurrogate `NRSur7dq4v2`, evaluated in geometric units with
`f_ref`, `f_low` (use `f_low = 0`, i.e. the full surrogate length, as long as it starts
before `f_ref`), `precessing_opts={'return_dynamics': True}`, dt = 0.1 M, returning the modes
h_lm(t) in the inertial frame that coincides with the LAL source frame at `f_ref`, and
`q_copr(t)`. The mode sum is h(t, n) = sum_lm h_lm(t) -2Y_lm(theta, phi) with gwsurrogate's
own spin-weighted harmonics.

**Peak time.** t* = argmax_t |h(t, N)|, refined by a cubic spline to 0.01 M. Report t*
relative to the surrogate's t = 0 (peak of the total amplitude, summed over modes).
v2 freezes the coprecessing frame between t = 0 and t = 20 M [@Ravishankar2026], so iota_Q
at t* > 0 is flagged as partly an artefact.

**Method 1.** z_copr(t*) = R(q_copr(t*)) z. iota_Q = arccos(z_copr . N).
Built-in check: iota_Q at `f_ref` equals the posterior `iota` to < 1e-3 rad.

**Method 2.** F(n) = |h(t*, n)| on a Fibonacci sphere grid of 20 000 points (~1.6 deg), the
largest value refined by Nelder-Mead to 1e-6 rad. F has two maxima near +-L. The emission
axis e is oriented, independently of method 1, by helicity: along +L the phase of h
decreases, so e is the maximum at which d arg h(t, e)/dt < 0 at t* (LAL convention; checked
in the S2 aligned-spin control). iota_E = arccos(e . N). Also report the second (opposite)
maximum and its angle from -e, which measures the emission asymmetry.

**Time series** (for plots, not for the answer): iota_Q(t) on the full grid; iota_E(t) from
t* - 1000 M to t* + 50 M at 1 M spacing, each time maximised from the previous time's axis.

**Rejected alternatives.**
- Newtonian L from BH trajectories: the surrogate does not model trajectories.
- Maximising |h| over time and direction jointly: the owner fixed the time as the peak
  along the line of sight.
- Using the Combined posterior: its maximum-likelihood point may belong to another
  waveform model with other conventions (owner's choice, 2026-09-25).

## Constraints

- Units: geometric (G = c = 1, times in total detector-frame mass M) inside the code;
  seconds only in plot labels where stated. Angles in radians internally, degrees in plots
  and reports. Masses: detector frame for the surrogate.
- Environment: a pixi project at the repo root (`pixi.toml`, `pixi.lock` tracked):
  python 3.11, numpy, scipy, h5py, matplotlib, pytest, lalsuite (conda-forge), gwsurrogate
  (PyPI, a version that has `NRSur7dq4v2`). The lock file is the environment record.
- Data: surrogate files, LAL data and the posterior go in `data/t01-merger-inclination/`
  (git-ignored); list them in `data/MANIFEST.yaml` with source URL and sha256.
  `config/site.local.yaml` does not exist yet; if a `scratch` path appears there, use it.
- Compute: minutes on the login node; no batch jobs (R06 does not apply at this size).
- Posterior: GWOSC links the GW231123 NRSur PE to Zenodo records 16004263 (2025-07-14,
  "CC5") and 17437902 (2025-10-28, "RR5"), file `posterior_samples.tar.gz` (~180 MB).
  Use 17437902 (the newer version). If the file holds more than one NRSur7dq4 label, run
  the pipeline for each and report each.
- Rules: R01 (state conventions before comparing), R02, R03, R04, R05 (every output
  records script, parameters, date, inputs; `provenance.yaml` beside results).
- Shared code in `src/`; no other task runs, so work on `main` without a worktree.
- Plots follow the `publication-plots` skill conventions but stay quick-look. Slack via the
  user's `slack` skill (channel set in that skill), authorised by the owner's request.

## Delegation

None. The subtasks are sequential; the main agent does all of them.

## Subtask S1: environment and data — main agent — ~30 min (±2×)

- Output directory: tasks/t01-merger-inclination/S1/
- Delivers: `pixi.toml`, `pixi.lock`; `data/t01-merger-inclination/` with the posterior h5,
  the gwsurrogate `NRSur7dq4v2` and `NRSur7dq4` data files, and LAL's `NRSur7dq4.h5`
  (lalsuite-extra) on `LAL_DATA_PATH`; `S1/inputs.md` with the chosen label(s), f_ref, the
  approximant string and the maximum-likelihood parameters as read from the file.
- Steps: install; download and checksum; read the h5 with h5py (no pesummary), pick the
  NRSur label(s), take argmax of `log_likelihood`, read f_ref from the stored config.
- Fatal if: the posterior has no NRSur7dq4 label, or gwsurrogate has no `NRSur7dq4v2`.

## Subtask S2: code, convention gate and controls — main agent — ~2 h (±2×)

- Output directory: tasks/t01-merger-inclination/S2/ (test output); code in
  `src/merger_inclination/` (`params.py` reading, `frames.py` N and rotations,
  `waveform.py` surrogate call and mode sum, `inclination.py` t*, iota_Q, iota_E,
  `cli.py` taking a PE file + label or a JSON of parameters), tests in `src/tests/`.
- Gate (convention; the load-bearing check): for the GW231123 maximum-likelihood sample,
  compute h_+ - i h_x from gwsurrogate `NRSur7dq4` (v1) modes summed at our N, and compare
  with `lalsimulation.SimInspiralChooseTDWaveform` for `NRSur7dq4` at the same parameters,
  same f_ref, phiRef = phase. Pass: after aligning the peak times, the relative L2 difference
  of the complex strain over [t* - 500 M, t* + 50 M] < 1e-2. Control that must fail: the same
  comparison with N built from (iota, phase) instead of (iota, pi/2 - phase), and with
  pi - iota, each must give > 1e-1. If LAL data cannot be obtained, compare instead with
  gwsurrogate's own `inclination`/`phi_ref` output and record the gate as weaker.
- Controls (pytest): (a) aligned spins (chi_z = 0.5, 0.3, q = 1.5, iota = 0.7, phase = 1.1):
  iota_Q(t) constant to 1e-6 rad, e = +z to 1e-3 rad, iota_E = iota_Q to 1e-3 rad; (b)
  iota_Q at f_ref equals input iota to 1e-3 rad for a precessing case; (c) face-on
  aligned case (iota = 0): e = +z and helicity sign negative; the same with iota = pi
  must give the opposite sign.
- Fatal if: the gate fails and two rounds of debugging (conventions first) find no cause.

## Subtask S3: GW231123 result and plots — main agent — ~30 min (±2×)

- Output directory: tasks/t01-merger-inclination/S3/
- Delivers: `S3/result_<label>_2026-MM-DD.json` (t*, t* in seconds from the total-amplitude
  peak, iota_Q, iota_E, the opposite-maximum angle, iota at f_ref, all inputs),
  `S3/provenance.yaml`, and three PDFs + PNGs per label:
  1. |h(t, N)| vs t/M with t* and t = 0 marked;
  2. iota_Q(t) and iota_E(t) vs t/M (from f_ref to +50 M, inset over the last 200 M) with
     the posterior iota at f_ref and t* marked;
  3. Mollweide map of |h(t*, n)| in the source frame with N, z_copr(t*), e, and z(f_ref)
     marked.
- Steps: run the CLI; make plots; send the PNGs and a 5-line summary (the two angles, t*,
  the f_ref used, the label) to Slack.

## Escalate only if fatal

- The GWOSC/Zenodo NRSur posterior lacks the Cartesian spins or f_ref: stop and report.
- gwsurrogate's inertial frame does not coincide with the LAL source frame at f_ref and no
  documented rotation fixes it (the gate cannot pass): stop and report.
- The ML sample lies outside the NRSur7dq4v2 training range so that gwsurrogate refuses it:
  report it with the value; do not extrapolate silently.

## Budget

S1 30 min, S2 2 h, S3 30 min; total ~3 h of agent time, compute negligible. Ceiling: 8 h
or 10 GB of downloads.
