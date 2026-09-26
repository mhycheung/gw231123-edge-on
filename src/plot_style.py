"""Publication plot style helpers (project-agnostic).

Copied from the author's publication-plots style module so that the plot scripts run from
this repo alone (src/ is on PYTHONPATH in the pixi environment).

Usage:
    import matplotlib
    matplotlib.use("Agg")  # on the cluster (no display)
    from plot_style import apply_style, StyleMap, LINEWIDTH, FILL_ALPHA

    apply_style()
    ax.plot(x, y, color=..., linestyle=..., linewidth=LINEWIDTH)
"""

import os

import matplotlib.pyplot as plt

# Defaults common to every figure in a paper
LINEWIDTH = 2.0
FILL_ALPHA = 0.2
LABEL_FONTSIZE = 16   # axis labels
TICK_LABELSIZE = 14   # tick labels
LEGEND_FONTSIZE = 14  # legend / in-plot annotations
SAVE_DPI = 200

# Default categorical color cycle to draw from when a project has no fixed scheme.
# A baseline / reference / null case is conventionally black; variants take C0, C1, C2, ...
DEFAULT_COLORS = ["black", "C0", "C1", "C2", "C3", "C4"]

# Distinguish a second, orthogonal categorical axis by linestyle, not color.
DEFAULT_LINESTYLES = ["-", "--", "-.", ":"]

def _site_texlive_bin():
    """The texlive bin dir for text.usetex rendering, or None if LaTeX is already on PATH.

    Read from the environment variable TEXLIVE_BIN_PATH, else from `texlive_bin` in the
    git-ignored config/site.local.yaml (run from the repo root).
    """
    if os.environ.get("TEXLIVE_BIN_PATH"):
        return os.environ["TEXLIVE_BIN_PATH"]
    try:
        with open("config/site.local.yaml") as f:
            for line in f:
                if line.startswith("texlive_bin:"):
                    return line.split(":", 1)[1].split("#")[0].strip().strip("'\"") or None
    except OSError:
        pass
    return None


TEXLIVE_BIN_PATH = _site_texlive_bin()


def ensure_latex(texlive_bin_path=TEXLIVE_BIN_PATH):
    """Prepend a texlive bin dir to PATH so text.usetex can find latex."""
    if not texlive_bin_path:
        return
    if texlive_bin_path not in os.environ.get("PATH", ""):
        os.environ["PATH"] = texlive_bin_path + ":" + os.environ.get("PATH", "")


def apply_style(usetex=True, figsize=(12, 10), texlive_bin_path=TEXLIVE_BIN_PATH):
    """Apply the publication rcParams. Call once at the top of a plotting script.

    Set usetex=False if LaTeX is unavailable in the environment.
    """
    plt.style.use("default")
    plt.rcParams["figure.figsize"] = list(figsize)
    plt.rcParams["font.size"] = 12
    plt.rcParams["text.usetex"] = usetex
    plt.rcParams["text.latex.preamble"] = r"\usepackage{amsmath}"
    # Ticks on all sides, pointing inward, minor ticks visible
    plt.rcParams["xtick.top"] = True
    plt.rcParams["xtick.bottom"] = True
    plt.rcParams["ytick.left"] = True
    plt.rcParams["ytick.right"] = True
    plt.rcParams["xtick.labeltop"] = False
    plt.rcParams["xtick.labelbottom"] = True
    plt.rcParams["ytick.labelleft"] = True
    plt.rcParams["ytick.labelright"] = False
    plt.rcParams["xtick.direction"] = "in"
    plt.rcParams["ytick.direction"] = "in"
    plt.rcParams["xtick.minor.visible"] = True
    plt.rcParams["ytick.minor.visible"] = True
    plt.rcParams["xtick.labelsize"] = TICK_LABELSIZE
    plt.rcParams["ytick.labelsize"] = TICK_LABELSIZE
    plt.rcParams["axes.grid"] = True
    plt.rcParams["grid.alpha"] = 0.3
    plt.rcParams["grid.linewidth"] = 0.5

    if usetex:
        ensure_latex(texlive_bin_path)


class StyleMap:
    """Fixed, reproducible mapping from result names to color and linestyle.

    Define ONE of these per project and reuse it in every figure so a given
    quantity keeps the same color across the whole paper.

        style = StyleMap(
            colors={"baseline": "black", "modelA": "C0", "modelB": "C1"},
            linestyles={"high_res": "-", "low_res": "--"},
        )
        style.color("modelA_high_res")      # -> 'C0'
        style.linestyle("modelA_high_res")  # -> '-'

    Keys are matched as substrings of the result name, longest key first, so
    composite names like 'modelA_high_res_run3' resolve without extra bookkeeping.
    """

    def __init__(self, colors, linestyles=None, labels=None, default_linestyle="-"):
        self.colors = dict(colors)
        self.linestyles = dict(linestyles or {})
        self.labels = dict(labels or {})
        self.default_linestyle = default_linestyle

    @staticmethod
    def _lookup(name, table, what):
        for key in sorted(table, key=len, reverse=True):
            if key in name:
                return table[key]
        raise KeyError(f"No {what} defined for result name: {name!r}")

    def color(self, name):
        return self._lookup(name, self.colors, "color")

    def linestyle(self, name):
        if not self.linestyles:
            return self.default_linestyle
        try:
            return self._lookup(name, self.linestyles, "linestyle")
        except KeyError:
            return self.default_linestyle

    def label(self, name):
        if self.labels:
            try:
                return self._lookup(name, self.labels, "label")
            except KeyError:
                pass
        return self._lookup(name, {k: k for k in self.colors}, "label")

    def kwargs(self, name, **extra):
        """Plot kwargs for a result name: color, linestyle, linewidth, label."""
        out = dict(
            color=self.color(name),
            linestyle=self.linestyle(name),
            linewidth=LINEWIDTH,
            label=self.label(name),
        )
        out.update(extra)
        return out


def save(fig, path, dpi=SAVE_DPI):
    """Save a publication figure.

    Deliberately does NOT pass bbox_inches='tight': that re-scales the canvas and
    misaligns rasterized layers against vector overlays. Set fig.dpi = dpi BEFORE
    creating any rasterized element.
    """
    fig.canvas.draw()
    if fig.dpi != dpi:
        raise AssertionError(f"Figure DPI ({fig.dpi}) doesn't match save DPI ({dpi})")
    fig.savefig(path, facecolor="white", dpi=dpi)
    return path
