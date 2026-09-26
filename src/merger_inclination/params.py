"""Read BBH parameters from a PESummary h5 file (with h5py) or a JSON file."""

import json

import h5py
import numpy as np

FIELDS = ["mass_1", "mass_2", "spin_1x", "spin_1y", "spin_1z", "spin_2x", "spin_2y",
          "spin_2z", "iota", "phase", "luminosity_distance"]


def _scalar(ds):
    v = ds[()]
    v = v[0] if np.ndim(v) else v
    return v.decode() if isinstance(v, bytes) else v


def read_pe_sample(path, label, index=None):
    """Parameters of one sample of `label`; default the maximum-likelihood sample.

    f_ref and the approximant are read from the file (R04), never assumed.
    Returns a dict with the FIELDS, 'f_ref' (Hz), 'approximant', 'index', 'log_likelihood'.
    """
    with h5py.File(path, "r") as f:
        g = f[label]
        ps = g["posterior_samples"][()]
        if index is None:
            index = int(np.argmax(ps["log_likelihood"]))
        out = {k: float(ps[k][index]) for k in FIELDS}
        out["log_likelihood"] = float(ps["log_likelihood"][index])
        f_ref = float(_scalar(g["meta_data/meta_data/f_ref"]))
        f_ref_cfg = float(_scalar(g["config_file/config/reference_frequency"]))
        assert f_ref == f_ref_cfg, (f_ref, f_ref_cfg)
        out["f_ref"] = f_ref
        out["approximant"] = str(_scalar(g["approximant"]))
    out["index"] = index
    out["label"] = label
    out["source"] = str(path)
    return out


def read_json(path):
    with open(path) as fh:
        p = json.load(fh)
    missing = [k for k in FIELDS[:-1] + ["f_ref"] if k not in p]
    if missing:
        raise KeyError(f"missing parameters: {missing}")
    return p
