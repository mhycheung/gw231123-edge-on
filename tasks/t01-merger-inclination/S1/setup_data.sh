#!/usr/bin/env bash
# Rebuild data/t01-merger-inclination/ (S1 of tasks/t01-merger-inclination/plan.md) and link
# the surrogate files where gwsurrogate and LAL look for them. Run from the repo root after
# `pixi install`. Checksums: md5 as published on Zenodo.
set -euo pipefail
D=data/t01-merger-inclination
mkdir -p "$D/surrogates" "$D/lal_data"
get() { # url dest md5
  [ -f "$2" ] || curl -sSL -o "$2" "$1"
  echo "$3  $2" | md5sum -c -
}
get https://zenodo.org/api/records/17437902/files/posterior_samples.tar.gz/content "$D/posterior_samples.tar.gz" 0e7f0f555d68c5cded1c9f04f49fd4a5
[ -f "$D/posterior_samples.h5" ] || tar xzf "$D/posterior_samples.tar.gz" -C "$D"
get https://zenodo.org/record/3348115/files/NRSur7dq4.h5 "$D/surrogates/NRSur7dq4.h5" 8e033ba4e4da1534b3738ae51549fb98
get https://zenodo.org/records/22257361/files/NRSur7dq4v2.h5 "$D/surrogates/NRSur7dq4v2.h5" 2bef4cfdb12d73904bd727015bef629c
get https://zenodo.org/api/records/14999310/files/NRSur7dq4_v1.0.h5/content "$D/lal_data/NRSur7dq4_v1.0.h5" ec4a0a9c6af39ad14dc91d42957144e9
SD=$(pixi run python -c "import gwsurrogate;print(gwsurrogate.catalog.download_path())" 2>/dev/null | tail -1)
mkdir -p "$SD"
for f in NRSur7dq4.h5 NRSur7dq4v2.h5; do ln -sf "$PWD/$D/surrogates/$f" "$SD/$f"; done
# LAL_DATA_PATH is set to $D/lal_data by pixi.toml [activation.env].
