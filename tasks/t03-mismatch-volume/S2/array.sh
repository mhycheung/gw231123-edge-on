#!/usr/bin/env bash
# SLURM array task for t03 S2: one chunk per SLURM_ARRAY_TASK_ID. Run from the repo root.
# Account, partition, time and array range are given at submission (see S2/run.md), from
# config/site.local.yaml. Environment: CHUNK (points per chunk), N_WIN, N_POST, N_FAC (points
# of the window set rerun with steps halved, the step check; one chunk of CHUNK points).
#SBATCH -J t03-metric
#SBATCH -n 1
#SBATCH -c 1
#SBATCH --mem=2G
set -euo pipefail
: "${CHUNK:?}" "${N_WIN:?}" "${N_POST:?}"
id=${SLURM_ARRAY_TASK_ID:?}
n_win=$(( (N_WIN + CHUNK - 1) / CHUNK ))
n_post=$(( (N_POST + CHUNK - 1) / CHUNK ))
fac=1
if (( id < n_win )); then
  set_=win; k=$id
elif (( id < n_win + n_post )); then
  set_=post; k=$(( id - n_win ))
else
  set_=win; k=$(( id - n_win - n_post )); fac=0.5
fi
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
pixi run python -m mismatch_metric.batch --set "$set_" --chunk "$k" --size "$CHUNK" \
  --fac "$fac" --out data/t03-mismatch-volume
