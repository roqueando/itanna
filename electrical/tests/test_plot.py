"""Tests for the inline plotting utilities."""

import os
import glob
import matplotlib
matplotlib.use("Agg")  # Must be set before importing pyplot

import matplotlib.pyplot as plt
import numpy as np
from electrical.utils.plot import (
    inline_plot, figure, show_plot, subplots,
    set_ee_style, reset_counter,
)


def setup_function():
    """Clean up before each test."""
    reset_counter()
    # Remove any leftover plot files
    for f in glob.glob("itanna-plot-*.png"):
        os.remove(f)


def teardown_function():
    """Clean up after each test."""
    for f in glob.glob("itanna-plot-*.png"):
        os.remove(f)


def test_inline_plot_context_manager():
    """Test the context manager produces a file (no stdout print)."""
    setup_function()
    import io
    from contextlib import redirect_stdout

    f = io.StringIO()
    with redirect_stdout(f):
        with inline_plot():
            plt.plot([1, 2, 3], [1, 4, 9])
            plt.title("Test")

    # inline_plot no longer prints; just saves the file
    output = f.getvalue()
    assert output == ""
    assert os.path.exists("itanna-plot-001.png")


def test_figure_show_plot():
    """Test the figure/show_plot API returns filename, doesn't print."""
    setup_function()
    import io
    from contextlib import redirect_stdout

    f = io.StringIO()
    with redirect_stdout(f):
        figure()
        plt.plot([0, 1], [0, 1])
        result = show_plot()

    output = f.getvalue()
    # show_plot returns the filename, doesn't print it
    assert output == ""
    assert result == "itanna-plot-001.png"
    assert os.path.exists("itanna-plot-001.png")


def test_subplots():
    """Test subplots wrapper."""
    setup_function()
    fig, ax = subplots(figsize=(6, 4))
    assert fig is not None
    assert ax is not None
    ax.plot([1, 2, 3], [1, 4, 9])
    plt.close(fig)


def test_counter_increment():
    """Test that the counter increments correctly."""
    setup_function()

    # First plot — use show_plot which returns the filename
    figure()
    plt.plot([1], [1])
    r1 = show_plot()
    assert r1 == "itanna-plot-001.png"
    assert os.path.exists(r1)

    # Second plot
    figure()
    plt.plot([2], [2])
    r2 = show_plot()
    assert r2 == "itanna-plot-002.png"
    assert os.path.exists(r2)


def test_ee_style():
    """Test that EE style can be applied without errors."""
    set_ee_style()
    # Just verify it doesn't crash and sets some params
    assert matplotlib.rcParams["axes.grid"] is True
    assert matplotlib.rcParams["figure.facecolor"] == "white"
