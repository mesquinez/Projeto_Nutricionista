import os
import sys

import pytest
import tkinter as tk


_PYTHON_BASE = getattr(sys, "base_prefix", sys.prefix)
os.environ.setdefault("TCL_LIBRARY", os.path.join(_PYTHON_BASE, "tcl", "tcl8.6"))
os.environ.setdefault("TK_LIBRARY", os.path.join(_PYTHON_BASE, "tcl", "tk8.6"))

UI_TEST_FILES = {
    "test_patient_ui.py",
    "test_patient_ui_rapid.py",
    "test_patient_window_ui.py",
}


def _tk_is_available():
    try:
        root = tk.Tk()
        root.withdraw()
        root.destroy()
        return True
    except Exception:
        return False


TK_AVAILABLE = _tk_is_available()


def pytest_configure(config):
    config._tk_available = TK_AVAILABLE


def pytest_collection_modifyitems(config, items):
    if getattr(config, "_tk_available", False):
        return

    skip_ui = pytest.mark.skip(reason="Tkinter/Tcl indisponivel neste ambiente de teste")
    for item in items:
        if item.fspath.basename in UI_TEST_FILES:
            item.add_marker(skip_ui)


@pytest.fixture(autouse=True)
def mock_tk_for_headless(monkeypatch):
    if not TK_AVAILABLE:
        return

    original_init = tk.Tk.__init__

    def mock_init(self):
        original_init(self)
        self.withdraw()

    monkeypatch.setattr(tk.Tk, "__init__", mock_init)
