"""Command line: inclination at peak strain for one PE sample or a JSON of parameters.

pixi run python -m merger_inclination.cli --pe FILE --label LABEL --out result.json
pixi run python -m merger_inclination.cli --json params.json --out result.json
Writes the result JSON and, beside it, <out>.series.npz with the time series.
"""

import argparse
import datetime
import json
import subprocess

import numpy as np

from .defaults import DEFAULTS
from .inclination import compute
from .params import read_json, read_pe_sample
from .waveform import MTSUN_SI


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--pe", help="PESummary h5 file")
    src.add_argument("--json", help="JSON file of parameters")
    ap.add_argument("--label", help="label in the PE file")
    ap.add_argument("--index", type=int, help="sample index (default: max likelihood)")
    ap.add_argument("--model", default=DEFAULTS["model"])
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    p = read_pe_sample(a.pe, a.label, a.index) if a.pe else read_json(a.json)
    res, wf = compute(p, model=a.model)
    series = res.pop("_series")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                            text=True).stdout.strip()
    res.update({
        "inputs": p,
        "settings": dict(DEFAULTS, model=a.model),
        "M_total_det_Msun": p["mass_1"] + p["mass_2"],
        "t_star_s_from_t0": res["t_star_M"] * (p["mass_1"] + p["mass_2"]) * MTSUN_SI,
        "degrees": {k: float(np.degrees(res[k])) for k in
                    ("iota_Q", "iota_E", "iota_Q_at_t_ref", "iota_input",
                     "angle_e_opp_from_minus_e", "angle_e_zcopr")},
        "provenance": {"script": "src/merger_inclination/cli.py", "src_commit": commit,
                       "date": datetime.date.today().isoformat(),
                       "argv": vars(a)},
    })
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=1)
    np.savez(a.out.rsplit(".json", 1)[0] + ".series.npz", **series,
             modes=np.array(wf.modes), t=wf.t, H=wf.H, q_copr=wf.q_copr)
    print(json.dumps({k: v for k, v in res.items() if k not in ("inputs", "settings")},
                     indent=1))


if __name__ == "__main__":
    main()
