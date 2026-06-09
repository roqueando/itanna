"""
Plotting Utilities for Itanna
==============================

Matplotlib utilities for engineering plots in Jupyter notebooks
and org-babel (Emacs).

No automatic backend configuration — the environment (Jupyter, Emacs, or
script) is responsible for setting the matplotlib backend. This prevents
import-time hangs and conflicts.

For Jupyter, run this once per session:
    %matplotlib inline

Usage in Jupyter (VSCode):
    %matplotlib inline
    from electrical.utils.plot import figure, show_plot, plot_signals
    import matplotlib.pyplot as plt
    import numpy as np

    t = np.linspace(0, 1e-5, 100)
    figure(figsize=(8, 4))
    plt.plot(t, np.sin(2e6 * t))
    show_plot()

Usage in org-babel (Emacs):
    #+begin_src python :results value file :session *Python-EE* :exports both
    from electrical.utils.plot import figure, show_plot

    figure(figsize=(8, 4))
    plt.plot([1, 2, 3], [1, 4, 9])
    show_plot()
    #+end_src
"""

import io
import os
import sys
import warnings
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, List, Dict, Any

# ── Import matplotlib without setting backend ───────────────────────────
# The backend is configured by the environment (Jupyter inline, Emacs org-babel,
# or script). We do NOT set it here to avoid kernel hangs and import-time
# conflicts. See `setup_jupyter()` and `setup_script()` below for explicit setup.
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

# ── Environment detection (safe, no magic) ──────────────────────────────
_IN_JUPYTER = False
try:
    _ip = get_ipython()  # type: ignore[name-defined]
    if _ip and hasattr(_ip, "kernel"):
        _IN_JUPYTER = True
except NameError:
    pass

# ── Explicit setup functions ────────────────────────────────────────────

def setup_jupyter():
    """Configure matplotlib for Jupyter inline display.

    Call this once at the top of your Jupyter notebook if you haven't
    already used the %matplotlib inline magic.

    Sets the backend to 'inline' so plots render in notebook cells.
    """
    try:
        ip = get_ipython()  # type: ignore[name-defined]
        if ip is not None:
            ip.run_line_magic("matplotlib", "inline")
    except (ImportError, AttributeError, NameError):
        pass


def setup_script():
    """Configure matplotlib for non-interactive script usage.

    Uses the Agg (anti-grain geometry) backend which does not require
    a display server. Use this for org-babel or headless scripts.

    Suppresses the harmless "non-interactive" warning from plt.show().
    """
    matplotlib.use("Agg")
    warnings.filterwarnings("ignore", message=".*non-interactive.*cannot be shown.*")


# ── Auto-setup for non-Jupyter environments ────────────────────────────
# In org-babel or plain scripts, default to Agg backend so plots can be
# saved to files without a display server. In Jupyter, the user is
# responsible for calling %matplotlib inline or setup_jupyter().
if not _IN_JUPYTER:
    setup_script()


# ── Global counter for auto-named plots ──────────────────────────────────
_plot_counter = [0]


def _plot_output_dir() -> str:
    """Return the directory where plot files should be saved.

    Priority:
      1. ITANNA_PLOT_DIR environment variable (set by Emacs pre-execute hook)
      2. Current working directory
    """
    return os.environ.get("ITANNA_PLOT_DIR") or os.getcwd()


def _next_filename(ext: str = "png", output_dir: str | None = None) -> str:
    """Generate the next auto-named plot filename with an absolute path.

    Args:
        ext: File extension (default "png")
        output_dir: Output directory (defaults to `_plot_output_dir()`)

    Returns:
        Absolute path string for the plot file.
    """
    _plot_counter[0] += 1
    basename = f"itanna-plot-{_plot_counter[0]:03d}.{ext}"
    outdir = output_dir or _plot_output_dir()
    return os.path.join(outdir, basename)


# ── Context manager ──────────────────────────────────────────────────────

@contextmanager
def inline_plot(figsize=None, dpi=100, format="png", filename=None, output_dir=None):
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
        output_dir: Output directory (default: ITANNA_PLOT_DIR env var or CWD)
    """
    fig = plt.figure(figsize=figsize)
    yield
    fname = filename or _next_filename(format, output_dir=output_dir)
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


def show_plot(filename: Optional[str] = None, dpi: int = 100,
              format: str = "png", output_dir: Optional[str] = None) -> Optional[str]:
    """Save the current plot to a file and/or display it.

    Behaviour depends on the environment:

    - **Jupyter**: If `%matplotlib inline` was set, the figure is already
      displayed by Jupyter when the cell finishes. This function saves
      the plot to a file if `filename` is given. Returns the filename or None.

    - **org-babel (Emacs)**: Saves the figure to a file and returns the
      absolute path (auto-generates a name if none given). The return
      value becomes the block result for inline display.

    - **Script (Agg backend)**: Saves to file and returns the path.

    Usage:
        figure()
        plt.plot(t, y)
        show_plot()              # auto-name in org-babel, display in Jupyter
        show_plot("plot.png")    # specify filename

    Args:
        filename: Output filename (auto-generated if None in non-Jupyter mode).
        dpi: Resolution in dots per inch.
        format: Image format ("png", "svg", "pdf").
        output_dir: Output directory (default: ITANNA_PLOT_DIR env or CWD).

    Returns:
        Absolute path to saved file, or None if nothing was saved.
    """
    outdir = output_dir or _plot_output_dir()

    # Determine filename
    fname: Optional[str] = None
    if filename:
        fname = os.path.join(outdir, filename)
    elif not _IN_JUPYTER:
        # In org-babel/script, auto-generate a name
        fname = _next_filename(format, output_dir=outdir)

    # Save to file if we have a name
    if fname:
        plt.savefig(fname, dpi=dpi, format=format, bbox_inches="tight")

    # Close the figure
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


# ── Flexible Multi-Signal Plotting ─────────────────────────────────────

def plot_signals(
    t: np.ndarray,
    signals: List[Dict[str, Any]],
    title: str = "",
    xlabel: str = "Time (s)",
    figsize: tuple = (10, 6),
    filename: Optional[str] = None,
    output_dir: Optional[str] = None,
    dpi: int = 100,
    format: str = "png",
    grid: bool = True,
    legend: bool = True,
    **kwargs
) -> Optional[str]:
    """Plot multiple signals against a common time axis.

    Creates a matplotlib figure with each signal on its own subplot
    (stacked vertically), sharing the same time axis.

    Parameters
    ----------
    t : np.ndarray
        Common time array (s).
    signals : list of dict
        Each dict describes one signal:

        .. code-block:: python

            {
                "name": "Inductor Current",     # legend label
                "values": i_l,                  # array of values
                "ylabel": "Current (A)",        # y-axis label
                "color": "#268bd2",            # optional, matplotlib color
                "linestyle": "-",              # optional
                "linewidth": 2,                # optional
                "alpha": 1.0,                  # optional
            }

    title : str, optional
        Overall figure title.
    xlabel : str, optional
        X-axis label (default "Time (s)").
    figsize : tuple, optional
        Figure size (width, height) in inches (default (10, 6)).
    filename : str, optional
        Save to this filename. Auto-generated if None and not in Jupyter.
    output_dir : str, optional
        Output directory for the saved file.
    dpi : int, optional
        Figure resolution (default 100).
    format : str, optional
        Image format (default "png").
    grid : bool, optional
        Show grid (default True).
    legend : bool, optional
        Show legend (default True).

    Returns
    -------
    str or None
        Absolute path to the saved file, or None if nothing was saved.

    Examples
    --------
    .. code-block:: python

        import numpy as np
        from electrical.utils.plot import plot_signals

        t = np.linspace(0, 1/300e3, 200)
        i_l = 2.0 + 0.3 * np.sin(2*np.pi*300e3*t)
        v_out = 3.3 + 0.01 * np.sin(2*np.pi*300e3*t)

        plot_signals(t, [
            {"name": "Inductor Current", "values": i_l,
             "ylabel": "Current (A)", "color": "#268bd2"},
            {"name": "Output Voltage", "values": v_out,
             "ylabel": "Voltage (V)", "color": "#dc322f"},
        ], title="Buck Converter Waveforms")
    """
    n_signals = len(signals)
    if n_signals == 0:
        raise ValueError("At least one signal is required")

    # Create subplots: one row per signal, shared x-axis
    fig, axes = plt.subplots(n_signals, 1, figsize=figsize, sharex=True, **kwargs)

    # Ensure axes is iterable even with a single signal
    if n_signals == 1:
        axes = [axes]

    for i, sig in enumerate(signals):
        ax = axes[i]
        name = sig.get("name", f"Signal {i+1}")
        values = sig["values"]
        ylabel = sig.get("ylabel", "")
        color = sig.get("color", None)
        ls = sig.get("linestyle", "-")
        lw = sig.get("linewidth", 2)
        alpha = sig.get("alpha", 1.0)

        ax.plot(t, values, color=color, linestyle=ls,
                linewidth=lw, alpha=alpha, label=name)

        if ylabel:
            ax.set_ylabel(ylabel, fontsize=12)
        if grid:
            ax.grid(True, alpha=0.3)
        if legend and name:
            ax.legend(fontsize=10)

        # Format y-axis with SI prefixes
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, p: f"{x:.2g}")
        )

    # X-axis label on the bottom subplot only
    axes[-1].set_xlabel(xlabel, fontsize=12)

    # Overall title
    if title:
        fig.suptitle(title, fontsize=14, y=1.01)

    plt.tight_layout()

    # Use show_plot to handle display/save
    return show_plot(filename=filename, output_dir=output_dir,
                     dpi=dpi, format=format)


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
