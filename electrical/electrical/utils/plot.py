"""
Plotting Utilities for Itanna
==============================

Matplotlib configuration for inline plotting in org-babel.

By default, matplotlib tries to open interactive windows.
This module configures it to output inline PNG/SVG images
that org-babel can capture and display in the buffer.

Usage in org-babel:
    #+begin_src python :results output file :file plot.png :session *Python-EE*
    from electrical.utils.plot import inline_plot
    import matplotlib.pyplot as plt

    with inline_plot():
        plt.plot([1, 2, 3], [1, 4, 9])
        plt.title("Example Plot")
    #+end_src

Or with the simpler short form:
    #+begin_src python :results output file :file plot.png :session *Python-EE*
    from electrical.utils.plot import *

    figure()
    plt.plot([1, 2, 3], [1, 4, 9])
    plt.title("Example")
    show_plot()
    #+end_src

The magic is:
  - :results output file  → tells org-babel to expect a file result
  - :file plot.png         → saves the plot to a file and displays inline
  - plt.savefig()          → saves without opening a window
"""

import io
import os
import sys
from contextlib import contextmanager
from pathlib import Path

# ── Agg backend: no X11/display needed ───────────────────────────────────
# This must be set before importing matplotlib.pyplot
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.image as mpimg


# ── Global counter for auto-named plots ──────────────────────────────────
_plot_counter = [0]


def _next_filename(ext: str = "png") -> str:
    """Generate the next auto-named plot filename."""
    _plot_counter[0] += 1
    return f"itanna-plot-{_plot_counter[0]:03d}.{ext}"


# ── Context manager ──────────────────────────────────────────────────────

@contextmanager
def inline_plot(figsize=None, dpi=100, format="png", filename=None):
    """Context manager for inline org-babel plotting.

    Saves the plot to a file instead of showing a window.
    When used in an org-babel block with :results file, the
    image is displayed inline.

    Args:
        figsize: Figure size as (width, height) in inches
        dpi: Resolution in dots per inch
        format: Image format ("png", "svg", "pdf")
        filename: Output filename (auto-generated if None)

    Usage:
        with inline_plot():
            plt.plot(x, y)
            plt.title("My Plot")
    """
    fig = plt.figure(figsize=figsize)
    yield
    fname = filename or _next_filename(format)
    plt.savefig(fname, dpi=dpi, format=format, bbox_inches="tight")
    plt.close(fig)
    print(f"[[file:{fname}]]")


# ── Simplified API ───────────────────────────────────────────────────────

def figure(figsize=None):
    """Create a new figure. Call before plotting.

    Usage:
        figure()
        plt.plot(x, y)
        show_plot()
    """
    plt.figure(figsize=figsize)


def show_plot(filename=None, dpi=100, format="png"):
    """Save the current plot to a file and print the org-link.

    This replaces plt.show() and outputs an org-mode image link
    that org-babel can display inline.

    Args:
        filename: Output filename (auto-generated if None)
        dpi: Resolution
        format: Image format
    """
    fname = filename or _next_filename(format)
    plt.savefig(fname, dpi=dpi, format=format, bbox_inches="tight")
    plt.close()
    print(f"[[file:{fname}]]")


def subplots(*args, **kwargs):
    """Wrapper around plt.subplots that returns (fig, ax).

    Usage:
        fig, ax = subplots(figsize=(10, 6))
        ax.plot(x, y)
        show_plot()
    """
    return plt.subplots(*args, **kwargs)


# ── Cleanup ──────────────────────────────────────────────────────────────

def reset_counter():
    """Reset the plot counter (useful when starting a new notebook session)."""
    _plot_counter[0] = 0


# ── Default style for EE plots ───────────────────────────────────────────

def set_ee_style():
    """Apply a clean style suitable for engineering publications."""
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.grid": True,
        "grid.alpha": 0.3,
        "axes.labelsize": 12,
        "axes.titlesize": 14,
        "legend.fontsize": 10,
        "lines.linewidth": 2,
        "lines.markersize": 6,
        "font.family": "sans-serif",
    })


# Apply EE style by default
set_ee_style()
