"""
Plotting Utilities for Itanna
==============================

Matplotlib configuration for inline plotting in org-babel.

By default, matplotlib tries to open interactive windows.
This module configures it to output inline PNG/SVG images
that org-babel can capture and display in the buffer.

Usage in org-babel:
    #+begin_src python :results value file :session *Python-EE* :exports both
    from electrical.utils.plot import figure, show_plot
    import matplotlib.pyplot as plt

    figure(figsize=(8, 4))
    plt.plot([1, 2, 3], [1, 4, 9])
    plt.title("Example Plot")
    show_plot()
    #+end_src

The magic is:
  - :results value file  → captures the return value (filename)
                           and wraps it in [[file:...]] for inline display
  - show_plot()          → saves the plot to a file (no window) and
                           returns the filename for org-babel to display
  - No X11/display needed → uses matplotlib Agg backend
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

    Saves the plot to a file. Use `show_plot()` as the last
    expression to return the file link, or use the context
    manager for setup/teardown only (you still need to call
    `show_plot()` or let the return value be the link).

    Args:
        figsize: Figure size as (width, height) in inches
        dpi: Resolution in dots per inch
        format: Image format ("png", "svg", "pdf")
        filename: Output filename (auto-generated if None)
    """
    fig = plt.figure(figsize=figsize)
    yield
    fname = filename or _next_filename(format)
    plt.savefig(fname, dpi=dpi, format=format, bbox_inches="tight")
    plt.close(fig)


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
    """Save the current plot to a file and return the filename.

    This replaces plt.show(). Saves the figure and returns the filename.
    Intended for org-babel with :results value — the return value becomes
    the block result, and org-babel handles the [[file:...]] wrapping.

    Use the return value as the last expression in your code block:

        figure()
        plt.plot(x, y)
        show_plot('myplot.png')   # ← last expression, value is returned

    Args:
        filename: Output filename (auto-generated if None).
                  Use .png extension for inline display in org.
        dpi: Resolution in dots per inch
        format: Image format ("png", "svg", "pdf")

    Returns:
        String like "itanna-plot-001.png" — just the filename (no [[file:...]])
    """
    fname = filename or _next_filename(format)
    plt.savefig(fname, dpi=dpi, format=format, bbox_inches="tight")
    plt.close()
    return fname


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
