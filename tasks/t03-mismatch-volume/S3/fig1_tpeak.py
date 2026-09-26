"""t03 S3: figure 1 relabelled with iota_Q(t_peak), and the chi_p trend of s in each |cos iota| bin.

Run from the repo root: pixi run python tasks/t03-mismatch-volume/S3/fig1_tpeak.py
Same data and binning as figure 1 of aggregate.py; t = 0 is the peak of the total mode amplitude,
so iota_Q(0) = iota_Q(t_peak). Writes fig1_s_vs_cos_W_tpeak_<DATE>.{pdf,png} and chi_p_trend_<DATE>.json.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aggregate as A  # noqa: E402

L10 = np.log(10)


def main():
    W = A.load("win_0*.npz")
    assert not W["failed"].any()
    A.fig_s(W, f"{A.OUT}/fig1_s_vs_cos_W_tpeak_{A.DATE}", xlabel=r"$|\cos\iota_Q(t_{\rm peak})|$")

    # Split log s = log sqrt(det g^theta) + log(1/pi_theta) and take bin medians of each part,
    # to see whether the rise with chi_p is carried by the metric or by the prior density alone.
    c = np.abs(np.cos(W["iota_Q0"]))
    edges = np.linspace(0, 1, 7)
    parts = {"log10_s": W["log_s"], "log10_sqrt_det_g": 0.5 * W["logdet_g_theta"],
             "log10_inv_pi": -W["log_pi_theta"]}
    bins = A.chi_bins(W["chi_p"])
    out = {"cos_edges": edges.tolist(), "chi_p_bins": list(A.D.CHI_P_BINS), "median_by_chi_bin": {},
           "hi_minus_lo_median": {}}
    for name, q in parts.items():
        out["median_by_chi_bin"][name] = [
            [float(np.median(q[b & (c >= edges[i]) & ((c < edges[i + 1]) | (i == 5))]) / L10) for i in range(6)]
            for b in bins]
        # log10 of (median, highest chi_p bin) / (median, lowest), with a bootstrap 68 % interval
        out["hi_minus_lo_median"][name] = [
            [v / L10 for v in A.boot(lambda x, y: np.median(x) - np.median(y),
                                     q[bins[2] & m], q[bins[0] & m])]
            for m in [(c >= edges[i]) & ((c < edges[i + 1]) | (i == 5)) for i in range(6)]]
    json.dump(out, open(f"{A.OUT}/chi_p_trend_{A.DATE}.json", "w"), indent=1)
    print(json.dumps(out["hi_minus_lo_median"], indent=1))


if __name__ == "__main__":
    main()
