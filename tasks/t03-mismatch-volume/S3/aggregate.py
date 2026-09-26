"""t03 S3: aggregate the S2 chunks, compute R_edge, and make figures 1-4.

Run from the repo root: pixi run python tasks/t03-mismatch-volume/S3/aggregate.py
Needs data/t03-mismatch-volume/signal_norm_<DATE>.npz (S3/signal_norm.py) and
tasks/t03-mismatch-volume/S3/psi_scan_<DATE>.json (S3/psi_scan.py).
"""
import glob
import json
import sys

import numpy as np

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from plot_style import apply_style, save  # noqa: E402

sys.path.insert(0, "src")
from mismatch_metric import defaults as D  # noqa: E402

DATE = "2026-09-25"
DATA = "data/t03-mismatch-volume"
OUT = "tasks/t03-mismatch-volume/S3"
EDGE_DEG = 20.0
N_BOOT = 1000
RNG = np.random.default_rng(1)
KEYS = ("point", "x", "flags", "failed", "log_s", "logdet_g_theta", "log_pi_theta", "log_N_rho",
        "n_nuisance", "iota_Q0", "iota_Q0_v2", "chi_p", "cond_g_theta")
CHI_LABELS = [r"$0\le\chi_p<0.4$", r"$0.4\le\chi_p<0.7$", r"$0.7\le\chi_p\le1$"]
CHI_COLORS = ["C0", "C1", "C2"]


def load(pattern):
    fs = sorted(glob.glob(f"{DATA}/chunks/{pattern}"))
    d = {k: np.concatenate([np.load(f)[k] for f in fs]) for k in KEYS}
    o = np.argsort(d["point"])
    return {k: v[o] for k, v in d.items()}


def logmeanexp(a):
    m = a.max()
    return m + np.log(np.mean(np.exp(a - m)))


def boot(f, *arrays):
    """Statistic f and its bootstrap 16, 84 % percentiles; each array resampled on its own."""
    v = f(*arrays)
    b = [f(*[a[RNG.integers(0, len(a), len(a))] for a in arrays]) for _ in range(N_BOOT)]
    lo, hi = np.percentile(b, [16, 84])
    return float(v), float(lo), float(hi)


def r_edge(log_s, edge):
    """log R_edge from means, from medians and from means of log s, with 68 % intervals."""
    a, b = log_s[edge], log_s[~edge]
    if len(a) < 5 or len(b) < 5:
        return {"n_edge": int(len(a)), "n_non_edge": int(len(b))}
    return {
        "n_edge": int(len(a)), "n_non_edge": int(len(b)),
        "log_R_mean": boot(lambda x, y: logmeanexp(x) - logmeanexp(y), a, b),
        "log_R_median": boot(lambda x, y: np.median(x) - np.median(y), a, b),
        "dmean_log_s": boot(lambda x, y: np.mean(x) - np.mean(y), a, b),
        "top10_share_of_sum_edge": top_share(a, 10),
        "top10_share_of_sum_non_edge": top_share(b, 10),
    }


def top_share(log_s, k):
    s = np.sort(np.exp(log_s - log_s.max()))[::-1]
    return float(s[:k].sum() / s.sum())


def chi_bins(chi_p):
    e = D.CHI_P_BINS
    return [(chi_p >= e[i]) & ((chi_p < e[i + 1]) if i < len(e) - 2 else (chi_p <= e[i + 1]))
            for i in range(len(e) - 1)]


def cos_binned(S, sel, qty):
    """Per |cos iota_Q(0)| bin: log of mean and median of exp(qty), each with a 68 % interval."""
    c = np.abs(np.cos(S["iota_Q0"]))
    edges = np.linspace(0, 1, D.N_COS_BINS + 1)
    rows = []
    for i in range(D.N_COS_BINS):
        b = sel & (c >= edges[i]) & (c < edges[i + 1] if i < D.N_COS_BINS - 1 else c <= 1)
        a = qty[b]
        if len(a) < 10:
            rows.append({"n": int(len(a))})
            continue
        rows.append({"n": int(len(a)), "log_mean": boot(logmeanexp, a),
                     "log_median": boot(np.median, a)})
    return edges, rows


def edge_mask(S):
    return np.abs(np.degrees(S["iota_Q0"]) - 90) < EDGE_DEG


def summary_for(S, name):
    edge = edge_mask(S)
    onesided = np.char.find(S["flags"], "onesided") >= 0
    out = {"n": int(len(S["log_s"])), "failed": int(S["failed"].sum()),
           "nonfinite_log_s": int((~np.isfinite(S["log_s"])).sum()),
           "fraction_edge": float(edge.mean()), "fraction_onesided": float(onesided.mean()),
           "R_edge": {}, "R_edge_excluding_onesided": {}, "binned": {}}
    for lab, b in zip(["all"] + CHI_LABELS, [np.ones_like(edge)] + chi_bins(S["chi_p"])):
        key = lab if lab == "all" else lab.replace("$", "").replace("\\", "")
        out["R_edge"][key] = r_edge(S["log_s"][b], edge[b])
        m = b & ~onesided
        out["R_edge_excluding_onesided"][key] = r_edge(S["log_s"][m], edge[m])
        edges, rows_s = cos_binned(S, b, S["log_s"])
        _, rows_n = cos_binned(S, b, S["log_N_rho"])
        c = np.abs(np.cos(S["iota_Q0"]))
        nus = [float(S["n_nuisance"][b & (c >= edges[i]) & (c <= edges[i + 1])].mean())
               if np.any(b & (c >= edges[i]) & (c <= edges[i + 1])) else None
               for i in range(D.N_COS_BINS)]
        out["binned"][key] = {"cos_edges": edges.tolist(), "log_s": rows_s,
                              "log_N_rho": rows_n, "mean_n_nuisance": nus}
    return out


def fig_s(S, path, title_hist=False, xlabel=r"$|\cos\iota_Q(0)|$"):
    """Figure 1 (W) or 2 (P, with the |cos iota_Q(0)| histogram beneath)."""
    apply_style(figsize=(8, 8 if title_hist else 6))
    if title_hist:
        fig, (ax, axh) = plt.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": [3, 1]}, dpi=200)
    else:
        fig, ax = plt.subplots(dpi=200)
    c = np.abs(np.cos(S["iota_Q0"]))
    for lab, col, b in zip(CHI_LABELS, CHI_COLORS, chi_bins(S["chi_p"])):
        edges, rows = cos_binned(S, b, S["log_s"])
        mid = 0.5 * (edges[1:] + edges[:-1])
        for stat, ls in (("log_mean", "-"), ("log_median", "--")):
            ok = np.array([stat in r for r in rows])
            if not ok.any():
                continue
            v = np.array([r[stat] for r in rows if stat in r]) / np.log(10)
            ax.plot(mid[ok], v[:, 0], ls=ls, color=col, marker="o", ms=4,
                    label=lab if stat == "log_mean" else None)
            ax.fill_between(mid[ok], v[:, 1], v[:, 2], color=col, alpha=0.2, lw=0)
    ax.axvline(np.sin(np.radians(EDGE_DEG)), color="k", lw=1, ls=":")
    ax.set_ylabel(r"$\log_{10} s$ \ (mean: solid, median: dashed)", fontsize=16)
    ax.legend(fontsize=14, loc="upper right")
    if title_hist:
        axh.hist(c, bins=np.linspace(0, 1, 25), color="0.5", histtype="stepfilled", alpha=0.6)
        axh.set_ylabel("points", fontsize=16)
        axh.set_xlabel(xlabel, fontsize=16)
    else:
        ax.set_xlabel(xlabel, fontsize=16)
    ax.set_xlim(0, 1)
    save(fig, path + ".pdf")
    save(fig, path + ".png")
    plt.close(fig)


def fig_nrho(S, path):
    apply_style(figsize=(8, 8))
    fig, (a1, a2) = plt.subplots(2, 1, sharex=True, dpi=200)
    for lab, col, b in zip(CHI_LABELS, CHI_COLORS, chi_bins(S["chi_p"])):
        edges, rows = cos_binned(S, b, S["log_N_rho"])
        mid = 0.5 * (edges[1:] + edges[:-1])
        for stat, ls in (("log_mean", "-"), ("log_median", "--")):
            v = np.array([r[stat] for r in rows]) / np.log(10)
            a1.plot(mid, v[:, 0], ls=ls, color=col, marker="o", ms=4,
                    label=lab if stat == "log_mean" else None)
            a1.fill_between(mid, v[:, 1], v[:, 2], color=col, alpha=0.2, lw=0)
        c = np.abs(np.cos(S["iota_Q0"]))
        nus = [S["n_nuisance"][b & (c >= edges[i]) & (c <= edges[i + 1])].mean()
               for i in range(D.N_COS_BINS)]
        a2.plot(mid, nus, color=col, marker="o", ms=4)
    for a in (a1, a2):
        a.axvline(np.sin(np.radians(EDGE_DEG)), color="k", lw=1, ls=":")
    a1.set_ylabel(r"$\log_{10} N_\rho$", fontsize=16)
    a1.legend(fontsize=14)
    a2.set_ylabel(r"mean nuisance count", fontsize=16)
    a2.set_xlabel(r"$|\cos\iota_Q(0)|$", fontsize=16)
    a2.set_xlim(0, 1)
    save(fig, path + ".pdf")
    save(fig, path + ".png")
    plt.close(fig)


def fig_mechanism(S, rho2, scan, path):
    apply_style(figsize=(8, 6))
    fig, ax = plt.subplots(dpi=200)
    edge = edge_mask(S)
    hl = 0.5 * S["logdet_g_theta"] / np.log(10)
    lr = np.log10(rho2 / np.median(rho2))
    ax.scatter(lr[~edge], hl[~edge], s=3, color="0.6", alpha=0.5, rasterized=True,
               label=r"W, $|\iota_Q(0)-90^\circ|\ge20^\circ$")
    ax.scatter(lr[edge], hl[edge], s=3, color="C3", alpha=0.5, rasterized=True,
               label=r"W, $|\iota_Q(0)-90^\circ|<20^\circ$")
    for k, i in enumerate(scan["top_points"]):
        r = sorted([row for row in scan["rows"] if row["point"] == i], key=lambda z: z["rho2_1000Mpc"])
        ax.plot(np.log10(np.array([z["rho2_1000Mpc"] for z in r]) / np.median(rho2)),
                np.array([z["half_logdet"] for z in r]) / np.log(10), "k-o", ms=4, lw=1.5,
                label=r"$\psi$ varied alone (3 points)" if k == 0 else None)
    ax.set_xlabel(r"$\log_{10}\left[\langle h,h\rangle / {\rm median}\right]$ at fixed distance",
                  fontsize=16)
    ax.set_ylabel(r"$\log_{10}\sqrt{\det g^\theta}$", fontsize=16)
    ax.legend(fontsize=12, markerscale=3)
    save(fig, path + ".pdf")
    save(fig, path + ".png")
    plt.close(fig)


def main():
    W, P = load("win_0*.npz"), load("post_0*.npz")
    H = load("win_fac0.5_0*.npz")
    N = np.load(f"{DATA}/signal_norm_{DATE}.npz")
    scan = json.load(open(f"{OUT}/psi_scan_{DATE}.json"))
    np.savez(f"{DATA}/win_{DATE}.npz", **W, rho2_1000Mpc=N["win_rho2"])
    np.savez(f"{DATA}/post_{DATE}.npz", **P, rho2_1000Mpc=N["post_rho2"])

    summ = {"date": DATE, "edge_definition_deg": EDGE_DEG, "n_boot": N_BOOT,
            "note": "log_R values are natural logs; each entry [value, 16 %, 84 %]",
            "W": summary_for(W, "W"), "P": summary_for(P, "P")}

    # Step check (Deviation 2): the same 400 W points at normal and halved steps.
    W400 = {k: v[:400] for k, v in W.items()}
    assert np.array_equal(W400["point"], H["point"])
    d = H["logdet_g_theta"] - W400["logdet_g_theta"]
    summ["step_check_400"] = {
        "median_abs_dlogdet": float(np.median(np.abs(d))),
        "p95_abs_dlogdet": float(np.percentile(np.abs(d), 95)),
        "max_abs_dlogdet": float(np.abs(d).max()),
        "R_edge_normal_steps": r_edge(W400["log_s"], edge_mask(W400)),
        "R_edge_half_steps": r_edge(H["log_s"], edge_mask(H)),
    }

    # v1 - v2 iota_Q(0) for P.
    dv = np.degrees(P["iota_Q0"] - P["iota_Q0_v2"])
    summ["P"]["iota_Q0_v1_minus_v2_deg"] = {
        "median_abs": float(np.median(np.abs(dv))), "p95_abs": float(np.percentile(np.abs(dv), 95)),
        "max_abs": float(np.abs(dv).max()),
        "edge_classification_changes": int(np.sum(edge_mask(P) != (np.abs(np.degrees(P["iota_Q0_v2"]) - 90) < EDGE_DEG)))}

    # Signal-norm diagnostic (S3/signal_norm.py, S3/psi_scan.py).
    from scipy.stats import spearmanr
    diag = {}
    for name, S, key in (("W", W, "win"), ("P", P, "post")):
        r2 = N[f"{key}_rho2"]
        edge = edge_mask(S)
        top = np.argsort(S["log_s"])[::-1][:20]
        diag[name] = {
            "spearman_half_logdet_vs_log_rho2": float(spearmanr(S["logdet_g_theta"], np.log(r2))[0]),
            "median_rho2_edge_over_non_edge": float(np.median(r2[edge]) / np.median(r2[~edge])),
            "top20_rho2_over_median": [float(v) for v in r2[top] / np.median(r2)],
            "top20_rho2_over_psi_max": [float(v) for v in r2[top] / N[f"{key}_rho2_max"][top]],
            # Supplementary, not in the plan: score per unit prior probability with the distance
            # prior (uniform in volume) marginalised at fixed observed SNR, s / rho_ref^3.
            "R_edge_distance_weighted": r_edge(S["log_s"] - 1.5 * np.log(r2), edge),
        }
    diag["psi_scan_fits"] = scan["fits"]
    summ["signal_norm_diagnostic"] = diag

    json.dump(summ, open(f"{OUT}/summary_{DATE}.json", "w"), indent=1)

    fig_s(W, f"{OUT}/fig1_s_vs_cos_W_{DATE}")
    fig_s(P, f"{OUT}/fig2_s_vs_cos_P_{DATE}", title_hist=True)
    fig_nrho(W, f"{OUT}/fig3_Nrho_nuisance_W_{DATE}")
    fig_mechanism(W, N["win_rho2"], scan, f"{OUT}/fig4_logdet_vs_signal_norm_W_{DATE}")
    print(json.dumps({k: summ[k]["R_edge"] for k in ("W", "P")}, indent=1))


if __name__ == "__main__":
    main()
