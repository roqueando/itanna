"""
Standalone Executable Builder
===============================

Generate standalone executables from Python functions using Nuitka.

The builder wraps a function with a Tkinter or PySide6 GUI and compiles
it into a standalone binary.

Usage:
    from electrical.executable.builder import build_app, make_app

    def my_calculator():
        # ... tkinter/pyside code ...
        pass

    # Build standalone
    build_app(my_calculator, name="buck-calc", gui="tkinter")
"""

from .builder import build_app, make_app
