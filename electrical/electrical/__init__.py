"""
itanna-electrical — Electrical Engineering Python Package
===========================================================

Part of the Itanna Emacs distribution.

Provides modules for:
  - Power converter design (buck, boost, flyback, etc.)
  - Filter design
  - Circuit analysis
  - Standalone executable generation (Nuitka + Tkinter/PySide6)
  - And more

Usage (from within Emacs org-babel):
  #+begin_src python :session *Python-EE*
  from electrical.converter.buck import design_buck
  results = design_buck(12, 3.3, 2, 300e3, 0.01)
  #+end_src
"""

__version__ = "0.1.0"
__author__ = "Itanna EE"
