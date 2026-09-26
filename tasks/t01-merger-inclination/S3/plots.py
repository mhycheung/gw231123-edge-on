"""S3 plots of t01 (plan.md). Quick-look, publication-plots conventions.

Usage (repo root): pixi run python tasks/t01-merger-inclination/S3/plots.py
Reads S3/result_C00-NRSur7dq4_<model>_2026-09-25.json and .series.npz for both models;
writes S3/fig{1,2,3}_*.{pdf,png}.
"""

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from plot_style import StyleMap, apply_style, save, LINEWIDTH  # noqa: E402

from merger_inclination.frames import angles, fibonacci_sphere  # noqa: E402,F401
from merger_inclination.waveform import sYlm  # noqa: E402

D = "tasks/t01-merger-inclination/S3"
DATE = "2026-09-25"
MODELS = {"NRSur7dq4v2": "NRSur7dq4v2", "NRSur7dq4": "NRSur7dq4 (v1)"}
style = StyleMap(colors={"NRSur7dq4v2": "C0", "NRSur7dq4": "C1", "ref": "black"},
                 linestyles={"Q": "-", "E": "--", "ref": ":"})
apply_style(figsize=(8, 5.5))


def load(m):
    base = f"{D}/result_C00-NRSur7dq4_{m}_{DATE}"
    npz = f"data/t01-merger-inclination/S3/result_C00-NRSur7dq4_{m}_{DATE}.series.npz"
    return json.load(open(base + ".json")), np.load(npz)


def ylm(modes, th, ph):
    return np.stack([sYlm(-2, int(l), int(mm), th, ph) for l, mm in modes], axis=-1)


R = {m: load(m) for m in MODELS}

# Figure 1: |h(t, N)|
fig, ax = plt.subplots(dpi=200)
for m, (res, s) in R.items():
    th, ph = angles(np.array(res["N"]))
    h = s["H"] @ ylm(s["modes"], np.atleast_1d(th), np.atleast_1d(ph))[0]
    ax.plot(s["t"], np.abs(h), color=style.colors[m], lw=LINEWIDTH, label=MODELS[m])
    ax.axvline(res["t_star_M"], color=style.colors[m], lw=1, ls="--")
ax.axvline(0, color="black", lw=1, ls=":", label=r"$t=0$")
ax.set_xlim(-300, 80)
ax.set_xlabel(r"$t\,[M]$", fontsize=16)
ax.set_ylabel(r"$(r/M)\,|h_+ - i h_\times|$ along $\hat N$", fontsize=16)
ax.legend(fontsize=14, loc="upper left")
fig.tight_layout(pad=0.5)
save(fig, f"{D}/fig1_strain_amplitude_{DATE}.pdf")
save(fig, f"{D}/fig1_strain_amplitude_{DATE}.png")
plt.close(fig)

# Figure 2: iota_Q(t), iota_E(t); left full range, right the last ~200 M from t_ref
fig, axs = plt.subplots(1, 2, dpi=200, figsize=(11, 5.5), gridspec_kw={"width_ratios": [3, 2]})
iota0 = np.degrees(R["NRSur7dq4v2"][0]["iota_input"])
for a in axs:
    for m, (res, s) in R.items():
        c = style.colors[m]
        a.plot(s["t_Q"], np.degrees(s["iota_Q"]), color=c, ls="-", lw=LINEWIDTH,
               label=rf"$\iota_Q$, {MODELS[m]}")
        a.plot(s["t_E"], np.degrees(s["iota_E"]), color=c, ls="--", lw=LINEWIDTH,
               label=rf"$\iota_E$, {MODELS[m]}")
        a.axvline(res["t_star_M"], color=c, lw=1, ls="-.")
        a.axvline(res["t_ref_M"], color=c, lw=1, ls=":")
    a.axhline(iota0, color="black", ls=":", lw=1.5, label=r"$\iota$ at $f_{\rm ref}$ (PE)")
    a.set_xlabel(r"$t\,[M]$", fontsize=16)
axs[0].set_xlim(-1100, 60)
axs[1].set_xlim(-210, 55)
axs[0].set_ylabel(r"inclination $[^\circ]$", fontsize=16)
h, l = axs[0].get_legend_handles_labels()
fig.legend(h, l, fontsize=12, loc="lower center", ncol=3)
fig.tight_layout(pad=0.5, rect=(0, 0.13, 1, 1))
save(fig, f"{D}/fig2_inclination_vs_time_{DATE}.pdf")
save(fig, f"{D}/fig2_inclination_vs_time_{DATE}.png")
plt.close(fig)

# Figure 3: Mollweide map of |h(t*, n)|, one per model
from scipy.interpolate import CubicSpline  # noqa: E402

for m, (res, s) in R.items():
    hv = CubicSpline(s["t"], s["H"], axis=0)(res["t_star_M"])
    lon = np.linspace(-np.pi, np.pi, 361)
    lat = np.linspace(-np.pi / 2, np.pi / 2, 181)
    LON, LAT = np.meshgrid(lon, lat)
    F = np.abs(ylm(s["modes"], (np.pi / 2 - LAT).ravel(), LON.ravel()) @ hv).reshape(LAT.shape)
    fig = plt.figure(figsize=(9, 5.2))
    fig.dpi = 200
    ax = fig.add_subplot(projection="mollweide")
    pm = ax.pcolormesh(LON, LAT, F, shading="auto", cmap="viridis", rasterized=True)
    cb = fig.colorbar(pm, ax=ax, orientation="horizontal", pad=0.08, shrink=0.7)
    cb.set_label(r"$(r/M)\,|h(t^*, \hat n)|$", fontsize=14)
    marks = {r"$\hat N$": (res["N"], "*", "red"),
             r"$\hat z_{\rm copr}(t^*)$": (res["z_copr_t_star"], "o", "white"),
             r"$\hat e$": (res["e"], "X", "orange"),
             r"$\hat z(f_{\rm ref})$": ([0, 0, 1], "^", "magenta")}
    for lab, (v, mk, c) in marks.items():
        th, ph = angles(np.array(v))
        ax.plot(ph, np.pi / 2 - th, mk, color=c, ms=12, mec="black", label=lab, ls="none")
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=9)
    ax.legend(fontsize=11, loc="upper right", bbox_to_anchor=(1.12, 1.12))
    fig.tight_layout(pad=0.5)
    fig.canvas.draw()
    save(fig, f"{D}/fig3_emission_map_{m}_{DATE}.pdf")
    save(fig, f"{D}/fig3_emission_map_{m}_{DATE}.png")
    plt.close(fig)
print("done")
