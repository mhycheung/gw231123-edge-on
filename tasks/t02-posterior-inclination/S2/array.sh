#!/usr/bin/env bash
# SLURM array task for t02 S2: one chunk per SLURM_ARRAY_TASK_ID. Run from the repo root.
# Account, partition, time and array range are given at submission (see S2/run.md), from
# config/site.local.yaml. Environment: CHUNK (samples per chunk), N_POST, N_PRIOR.
#SBATCH -J t02-incl
#SBATCH -n 1
#SBATCH -c 1
#SBATCH --mem=2G
set -euo pipefail
: "${CHUNK:?}" "${N_POST:?}" "${N_PRIOR:?}"
id=${SLURM_ARRAY_TASK_ID:?}
n_post_chunks=$(( (N_POST + CHUNK - 1) / CHUNK ))
if (( id < n_post_chunks )); then
  set_=post; start=$(( id * CHUNK )); n=$N_POST
else
  set_=prior; start=$(( (id - n_post_chunks) * CHUNK )); n=$N_PRIOR
fi
stop=$(( start + CHUNK )); (( stop > n )) && stop=$n
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
pixi run python -m merger_inclination.batch \
  --pe data/t01-merger-inclination/posterior_samples.h5 --label C00:NRSur7dq4 \
  --set "$set_" --start "$start" --stop "$stop" --out data/t02-posterior-inclination/chunks
