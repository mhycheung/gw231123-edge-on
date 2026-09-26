---
status: done
---

# S3: aggregate, figures, result

Date: 2026-09-25. Commands (repo root): `pixi run python tasks/t03-mismatch-volume/S3/signal_norm.py` (37 s on 8 CPUs),
`pixi run python tasks/t03-mismatch-volume/S3/psi_scan.py` (35 s), `pixi run python tasks/t03-mismatch-volume/S3/aggregate.py`.
All numbers MEASURED from `summary_2026-09-25.json`; provenance in `provenance.yaml`.

## Outcome

- $R_{\rm edge}$ (ratio of medians, set W): 18.0 (68 %: 16.1–20.4); by $\chi_p$ bin 20.7, 16.5, 12.2. $>1$ at high significance,
  not rising with $\chi_p$. Result: `results/r-t03-edge-on-metric-volume.md`. Added 2026-09-25: the median of $s$ itself rises with $\chi_p$
  at every inclination (`fig1_tpeak.py`, `chi_p_trend_2026-09-25.json`, `results/r-t03-s-vs-inclination-figure.md`).
- The plan's $R_{\rm edge}$ (ratio of means): $1.9\times10^3$ (bootstrap 68 %: $1.1$–$3.4\times10^3$), not converged. The 10 largest points hold
  91 % of the edge-on sum and 73 % of the non-edge-on sum; the first 400 points alone give 7.4.
- Set P: ratio of medians 1.13 (1.03–1.21); the posterior samples do not favour high-$s$ orientations.
- Mechanism: the large $s$ values are orientations with weak network signal (figure 4). A controlled $\psi$-only test gives
  $\sqrt{\det g^\theta}\propto\langle h,h\rangle^{-3.8\ {\rm to}\ -4.5}$. Result: `results/r-t03-signal-norm-mechanism.md`.
- Step check (S1 deviation 2): halved steps change the ratio of medians of the 400-point subset from 6.93 to 6.66 and the ratio
  of means from 7.43 to 7.31. Closed.
- One-sided differences excluded: W 18.4, P 1.13. v1–v2 $\iota_Q(0)$ over P: median $0.44^\circ$, max $3.1^\circ$, 43 of 2001 points change class.
- $N_\rho$ median falls by about one decade from edge-on to face-on; all three nuisances resolved except near face-on (figure 3).
- Supplementary (not in the plan): with the distance prior marginalised at fixed observed SNR, the score becomes
  $s/\langle h,h\rangle^{3/2}$. Its ratio of medians is 119 (W) and 7.1 (P). This is for the user to decide on.

## Added to the plan

The signal-norm diagnostic (`signal_norm.py`, `psi_scan.py`, figure 4) was not planned. It was added because 10 of 8000
points held 91 % of the edge-on sum, and the reading of $R_{\rm edge}$ depends on what those points are.

## Files

| file | what |
|---|---|
| `aggregate.py` | aggregation, bootstrap, figures 1–4, `summary_2026-09-25.json` |
| `signal_norm.py` | $\langle h,h\rangle$ at 1000 Mpc per point, at the point's $\psi$, and its mean and maximum over $\psi$ |
| `psi_scan.py`, `psi_scan_2026-09-25.json` | controlled $\psi$-only test at 6 points |
| `fig1`–`fig4` (`.pdf`, `.png`, `.caption.md`) | $s$ vs $\lvert\cos\iota_Q(0)\rvert$ for W and P; $N_\rho$ and nuisance count; mechanism |
| `provenance.yaml` | commit, lock file, commands, checksums |
