---
status: done
---

# S2: full run as a SLURM job array

Date: 2026-09-25. Code commit at submission: `6ca7208` (batch module); record commit `6e19276`.

## Submission

From the repo root, account and partition from `config/site.local.yaml`:

```
sbatch --parsable --array=0-155 -A <account> -p <partition> -t 01:00:00 \
  -o data/t02-posterior-inclination/slurm/%A_%a.out \
  --export=ALL,CHUNK=150,N_POST=18185,N_PRIOR=5000 tasks/t02-posterior-inclination/S2/array.sh
```

One SLURM job array: 156 tasks, one CPU and 2 GB each. Tasks 0-121 are posterior chunks of 150
samples (the last is 18150-18185); tasks 122-155 are prior chunks.

## Outcome (MEASURED)

- Submitted 14:51:57; first task started 15:00:44; last task ended 15:35:34.
  Command: `sacct -j 20907281 -X -n -o Submit,Start,End,Elapsed`.
- 156/156 tasks COMPLETED (`sacct -j 20907281 -X -n -o State`); no `Error` or `Traceback` in
  the SLURM logs.
- Summed elapsed time 36.0 CPU-h; longest task 999 s (`sacct ... -o ElapsedRaw`). S1 predicted 38 CPU-h.
- 156 chunk files, 465 MB, in `data/t02-posterior-inclination/chunks/`.
- Sample indices: posterior 0-18184 and prior 0-4999, each present exactly once.
- `failed` flags: 0 of 18185 posterior samples, 0 of 5000 prior samples.

No resubmission was needed.
