---
status: done
---

# S1 inputs: GW231123 NRSur7dq4 maximum-likelihood sample

Made 2026-09-25 by the main agent (S1 of `../plan.md`). The data are rebuilt by
`setup_data.sh` (this directory); the package versions are recorded in `pixi.lock` at the repo root.

## Source

- File: `data/t01-merger-inclination/posterior_samples.h5`, from Zenodo record 17437902,
  `posterior_samples.tar.gz` (md5 `0e7f0f555d68c5cded1c9f04f49fd4a5`, matches Zenodo).
- Labels in the file: `C00:IMRPhenomTPHM`, `C00:IMRPhenomXO4a`,
  `C00:IMRPhenomXPHM-SpinTaylor`, `C00:Mixed`, `C00:NRSur7dq4`, `C00:SEOBNRv5PHM`.
  **One NRSur label: `C00:NRSur7dq4`** (18185 samples). The pipeline runs only this label.
- Approximant string (`C00:NRSur7dq4/approximant` and `config_file/config/waveform_approximant`):
  `NRSur7dq4`.
- f_ref = **10.0 Hz** (`meta_data/meta_data/f_ref`; `config/reference_frequency` = `10.0`;
  `meta_data/other/likelihood/waveform_arguments/reference_frequency` = `10.`).
- Waveform minimum frequency 0 (`config/minimum_frequency` = `{ H1:20,L1:20, waveform: 0 }`,
  `likelihood/waveform_arguments/minimum_frequency` = 0): the PE used the full surrogate length.
- Generator: `bilby.gw.waveform_generator.LALCBCWaveformGenerator` with
  `lal_binary_black_hole`, so the PE waveform is LALSimulation's `NRSur7dq4`.

## Maximum-likelihood sample (MEASURED)

Command: `np.argmax(ps['log_likelihood'])` over `C00:NRSur7dq4/posterior_samples` (h5py);
index 6096; no ties.

| field | value |
|---|---|
| log_likelihood | 218.1531172580967 |
| mass_1 (detector frame, Msun) | 156.9056031178424 |
| mass_2 (detector frame, Msun) | 142.76526938384222 |
| total_mass (detector frame, Msun) | 299.67087250168464 |
| mass_ratio m2/m1 | 0.9098799950223562 |
| spin_1x, spin_1y, spin_1z | -0.7507878610744102, -0.5992799028922391, -0.013782593921909204 |
| spin_2x, spin_2y, spin_2z | -0.059524426161772066, 0.9844048876525949, -0.029694242111677226 |
| a_1, a_2 | 0.9607334563979937, 0.9866498305674576 |
| tilt_1, tilt_2 (rad) | 1.5851427270670548, 1.600896901200118 |
| iota (rad) | 1.1227292632983898 |
| theta_jn (rad) | 1.3893612941425153 |
| phase (rad) | 1.9914967391382514 |
| luminosity_distance (Mpc) | 1121.4998157264695 |
| psi (rad) | 2.319660241513669 |
| geocent_time (s) | 1384782888.6186297 |
| network_matched_filter_snr | 21.1503999702982 |

Derived: M f_ref = 0.014760 (geometric, with M_sun = 4.925490947641267e-6 s), orbital
angular frequency at f_ref pi M f_ref = 0.04637 rad/M.

## Training range (MEASURED)

Both spin magnitudes exceed the NRSur7dq4 training range. gwsurrogate 1.2.0 warns and
does not refuse: `Spin magnitude of BhA=0.9607 is outside training range: chi<=0.8010`
(BhB = 0.9866, same text). The PE itself used these extrapolated waveforms (LAL
generates the waveform without error). The result is therefore a statement about the model as
extrapolated, the same model the PE used.

## Checks run (MEASURED)

- gwsurrogate `NRSur7dq4` and `NRSur7dq4v2` at the ML sample, `dt=0.1`, `f_low=0`,
  `f_ref=10 Hz x M` (geometric), `return_dynamics`: both return t in [-4300, 100] M, 21 and 32
  modes respectively, dynamics keys `chiA, chiB, chiA_copr, chiB_copr, q_copr, orbphase`.
- LALSimulation `SimInspiralChooseTDWaveform(NRSur7dq4)` at the ML sample, f_min = 0,
  f_ref = 10 Hz, dt = 1/4096 s: 26602 samples, epoch -6.347 s. LAL needs
  `NRSur7dq4_v1.0.h5` (lalsuite-waveform-data, Zenodo 14999310) on `LAL_DATA_PATH`.

Versions: gwsurrogate 1.2.0, lal 7.7.0, lalsimulation 6.2.0, numpy 2.4.6, scipy 1.17.1,
h5py 3.16.0, matplotlib 3.11.2, python 3.11.
