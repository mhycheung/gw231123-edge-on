"""t02 S3: aggregate the S2 chunks, compute the t = 0 numbers, and plot the bands.

Run from the repo root: pixi run python tasks/t02-posterior-inclination/S3/aggregate.py
"""
import glob
import json

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from plot_style import apply_style, save

DATE = "2026-09-25"
CHUNKS = "data/t02-posterior-inclination/chunks"
DATA_OUT = "data/t02-posterior-inclination"
OUT = "tasks/t02-posterior-inclination/S3"
SETS = {"post": 18185, "prior": 5000}
QS = [5, 16, 50, 84, 95]
COLOR = {"post": "C0", "prior": "C1"}
NAME = {"post": "posterior", "prior": "prior"}


def aggregate(s):
    files = sorted(glob.glob(f"{CHUNKS}/{s}_*.npz"))
    parts = [np.load(f) for f in files]
    keys = [k for k in parts[0].files if k not in ("T_Q", "T_E", "model")]
    out = {k: np.concatenate([p[k] for p in parts]) for k in keys}
    order = np.argsort(out["index"])
    out = {k: v[order] for k, v in out.items()}
    assert np.array_equal(out["index"], np.arange(SETS[s])), s
    for k in ("T_Q", "T_E", "model"):
        assert all(np.array_equal(p[k], parts[0][k]) for p in parts), k
        out[k] = parts[0][k]
    np.savez(f"{DATA_OUT}/{s}_{DATE}.npz", **out)
    return out


def interval(x):
    lo, med, hi = np.percentile(x, [5, 50, 95])
    return {"median": med, "lo90": lo, "hi90": hi}


def numbers(d):
    ok = ~d["failed"]
    res = {"n": int(len(ok)), "n_failed": int((~ok).sum())}
    for name, x in [("iota_fref", d["iota_input"]), ("iota_Q0", d["iota_Q0"]),
                    ("iota_E0", d["iota_E0"])]:
        deg = np.degrees(x[ok])
        r = interval(deg)
        r["P_within10_of_90"] = float(np.mean(np.abs(deg - 90) < 10))
        r["P_within20_of_90"] = float(np.mean(np.abs(deg - 90) < 20))
        res[name + "_deg"] = {k: float(v) for k, v in r.items()}
    h = d["helicity_E"][ok]
    res["helicity_flip_fraction"] = float(np.mean(np.any(h > 0, axis=1)))
    res["helicity_ambiguous_t0_fraction"] = float(np.mean(d["helicity_ambiguous0"][ok]))
    res["t_ref_M"] = {k: float(v) for k, v in interval(d["t_ref"][ok]).items()}
    return res


def band_plot(D):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True, dpi=200,
                             gridspec_kw={"width_ratios": [2, 1.2], "wspace": 0.05})
    for ax, (x0, x1) in zip(axes, [(-4300, 100), (-250, 50)]):
        for s, d in D.items():
            ok = ~d["failed"]
            for key, T, ls in [("iota_Q", d["T_Q"], "-"), ("iota_E", d["T_E"], "--")]:
                q = np.degrees(np.percentile(d[key][ok], QS, axis=0))
                ax.fill_between(T, q[0], q[4], color=COLOR[s], alpha=0.12, lw=0)
                ax.fill_between(T, q[1], q[3], color=COLOR[s], alpha=0.2, lw=0)
                ax.plot(T, q[2], color=COLOR[s], ls=ls, lw=2.0)
        tr = np.percentile(D["post"]["t_ref"], [5, 50, 95])
        ax.axvspan(tr[0], tr[2], color="gray", alpha=0.15, lw=0)
        ax.axvline(tr[1], color="gray", lw=1.0)
        ax.axhline(90, color="k", lw=0.8, ls=":")
        ax.set_xlim(x0, x1)
        ax.set_xlabel(r"$t/M$", fontsize=16)
    # posterior iota at f_ref as a band on the left edge of the left panel
    fr = np.degrees(np.percentile(D["post"]["iota_input"], QS))
    x0 = -4300
    axes[0].fill_between([x0, x0 + 60], fr[0], fr[4], color="k", alpha=0.2, lw=0)
    axes[0].fill_between([x0, x0 + 60], fr[1], fr[3], color="k", alpha=0.3, lw=0)
    axes[0].plot([x0, x0 + 60], [fr[2]] * 2, color="k", lw=2.0)
    axes[0].set_ylabel(r"$\iota\ [\mathrm{deg}]$", fontsize=16)
    axes[0].set_ylim(0, 180)
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    handles = [Line2D([], [], color="C0", lw=2, label="posterior"),
               Line2D([], [], color="C1", lw=2, label="prior"),
               Line2D([], [], color="gray", lw=2, ls="-", label=r"$\iota_Q$"),
               Line2D([], [], color="gray", lw=2, ls="--", label=r"$\iota_E$"),
               Patch(color="k", alpha=0.3, label=r"posterior $\iota$ at $f_\mathrm{ref}$"),
               Patch(color="gray", alpha=0.3, label=r"posterior $t_\mathrm{ref}$")]
    axes[1].legend(handles=handles, fontsize=12, loc="upper left", ncol=2)
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.12, top=0.97)
    for ext in ("pdf", "png"):
        save(fig, f"{OUT}/bands_{DATE}.{ext}")
    plt.close(fig)


def hist_plot(D):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), sharey=True, dpi=200,
                             gridspec_kw={"wspace": 0.05})
    bins = np.linspace(0, 180, 61)
    for ax, key, lab in [(axes[0], "iota_Q0", r"$\iota_Q(t=0)$"),
                         (axes[1], "iota_E0", r"$\iota_E(t=0)$")]:
        for s, d in D.items():
            ok = ~d["failed"]
            ax.hist(np.degrees(d[key][ok]), bins=bins, density=True, histtype="stepfilled",
                    color=COLOR[s], alpha=0.2)
            ax.hist(np.degrees(d[key][ok]), bins=bins, density=True, histtype="step",
                    color=COLOR[s], lw=2.0, label=f"{NAME[s]}, {lab}")
            ax.hist(np.degrees(d["iota_input"][ok]), bins=bins, density=True,
                    histtype="step", color="k", lw=1.5, ls="-" if s == "post" else ":",
                    label=rf"{NAME[s]}, $\iota$ at $f_\mathrm{{ref}}$")
        ax.axvline(90, color="k", lw=0.8, ls="--")
        ax.set_xlim(0, 180)
        ax.set_xlabel(lab + r"$\ [\mathrm{deg}]$", fontsize=16)
        ax.legend(fontsize=12, loc="upper left")
    axes[0].set_ylabel(r"density $[\mathrm{deg}^{-1}]$", fontsize=16)
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.12, top=0.97)
    for ext in ("pdf", "png"):
        save(fig, f"{OUT}/t0_hist_{DATE}.{ext}")
    plt.close(fig)


def folded_band_plot(D):
    """Supplementary: pointwise bands of |iota - 90 deg|, the distance from edge-on.
    iota itself is bimodal about 90 deg for the posterior, so its pointwise median lies
    between the modes; the folded angle is unimodal."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True, dpi=200,
                             gridspec_kw={"width_ratios": [2, 1.2], "wspace": 0.05})
    for ax, (x0, x1) in zip(axes, [(-4300, 100), (-250, 50)]):
        for s, d in D.items():
            ok = ~d["failed"]
            for key, T, ls in [("iota_Q", d["T_Q"], "-"), ("iota_E", d["T_E"], "--")]:
                q = np.percentile(np.abs(np.degrees(d[key][ok]) - 90), QS, axis=0)
                if ls == "-":
                    ax.fill_between(T, q[1], q[3], color=COLOR[s], alpha=0.2, lw=0)
                ax.plot(T, q[2], color=COLOR[s], ls=ls, lw=2.0)
                ax.plot(T, q[4], color=COLOR[s], ls=ls, lw=1.0)
        tr = np.percentile(D["post"]["t_ref"], [5, 50, 95])
        ax.axvspan(tr[0], tr[2], color="gray", alpha=0.15, lw=0)
        ax.axvline(tr[1], color="gray", lw=1.0)
        ax.set_xlim(x0, x1)
        ax.set_xlabel(r"$t/M$", fontsize=16)
    fr = np.percentile(np.abs(np.degrees(D["post"]["iota_input"]) - 90), QS)
    x0 = -4300
    axes[0].fill_between([x0, x0 + 60], fr[1], fr[3], color="k", alpha=0.3, lw=0)
    axes[0].plot([x0, x0 + 60], [fr[2]] * 2, color="k", lw=2.0)
    axes[0].set_ylabel(r"$|\iota - 90^\circ|\ [\mathrm{deg}]$", fontsize=16)
    axes[0].set_ylim(0, 90)
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    handles = [Line2D([], [], color="C0", lw=2, label="posterior"),
               Line2D([], [], color="C1", lw=2, label="prior"),
               Line2D([], [], color="gray", lw=2, ls="-", label=r"$\iota_Q$ (68\,\% shaded)"),
               Line2D([], [], color="gray", lw=2, ls="--", label=r"$\iota_E$"),
               Line2D([], [], color="gray", lw=1, label=r"95th percentile"),
               Patch(color="k", alpha=0.3, label=r"posterior at $f_\mathrm{ref}$")]
    axes[1].legend(handles=handles, fontsize=12, loc="upper left", ncol=2)
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.12, top=0.97)
    for ext in ("pdf", "png"):
        save(fig, f"{OUT}/folded_bands_{DATE}.{ext}")
    plt.close(fig)


if __name__ == "__main__":
    apply_style()
    D = {s: aggregate(s) for s in SETS}
    summary = {s: numbers(d) for s, d in D.items()}
    with open(f"{OUT}/summary_{DATE}.json", "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))
    band_plot(D)
    hist_plot(D)
    folded_band_plot(D)
