---
status: done
---

# S2: full run as a SLURM job array

Date: 2026-09-25. Code commit at submission: `b79cf2b`.

## Submission

From the repo root, account and partition from `config/site.local.yaml`:

```
sbatch --parsable --array=0-26 -A <account> -p <partition> -t 01:00:00 \
  -o data/t03-mismatch-volume/slurm/%A_%a.out \
  --export=ALL,CHUNK=400,N_WIN=8000,N_POST=2001 tasks/t03-mismatch-volume/S2/array.sh
```

One SLURM job array, submitted 20:36:44: 27 tasks, one CPU and 2 GB each. Tasks 0-19: window
chunks `win_0000`-`win_0019` (400 points each); tasks 20-25: posterior chunks
`post_0000`-`post_0005` (the last holds point 2000, the ML sample); task 26: the step check,
window points 0-399 with steps halved (`win_fac0.5_0000`). Point sets:
`data/t03-mismatch-volume/{win,post}_points.npz` (seed 1). Expected ~20 min per task (S1:
2.2-2.7 s per point).

Check: `sacct -j 20909319 -X -n -o JobID,State,Elapsed | sort | uniq -c -f1`;
`ls data/t03-mismatch-volume/chunks/ | wc -l` (27 when done).

## Outcome

All 27 tasks COMPLETED with exit code 0 (`sacct -j 20909319 -X -n -o JobID,State,Elapsed,ExitCode`);
started 20:36-20:38, last chunk written 20:52. Elapsed per task 8:12-10:37 for the 400-point
chunks, 14:34 for task 2, 0:36 for task 25 (one point). No resubmission was needed.

Per-point outcome, MEASURED from the chunk files (`failed`, `flags`, `cond_g_theta`, `seconds`):

| set | points | unique indices | failed | non-finite $\log s$ | cond $g^\theta$ max (median) | one-sided differences | `iota_near_pole` | CPU time |
|---|---|---|---|---|---|---|---|---|
| W | 8000 | 0-7999 | 0 | 0 | $5.1\times10^{4}$ ($5.8\times10^{2}$) | 3.3 % | 40 | 2.96 h, median 1.23 s per point |
| P | 2001 | 0-2000 | 0 | 0 | $2.6\times10^{4}$ ($7.3\times10^{2}$) | 21.0 % | 0 | 0.75 h |
| W, steps halved | 400 | 0-399 | 0 | 0 | | | | |

- The fatal condition of S2 (failures > 1 %) is not met: 0 failures. The escalation condition on
  conditioning (cond $g^\theta>10^{12}$ at > 5 % of W) is not met: the maximum is $5.1\times10^4$.
- One-sided differences are more frequent than S1 estimated (W 0.7 %, P 5.5 %): P's spins lie near
  $|\chi|=0.99$ and $q$ near 1. S3 reports $R_{\rm edge}$ with and without these points.
- All chunks record `src_commit` `1a5ba14`; `git diff b79cf2b 1a5ba14 -- src` is empty, so the code
  is the S1 code. SLURM logs contain no error or traceback (`grep -il -E 'error|traceback' ...`).
- Total 3.7 CPU-h, against ~40 CPU-h budgeted: points ran at 1.2 s instead of S1's 2.7 s (S1 ran
  on a loaded node).
