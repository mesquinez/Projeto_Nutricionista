import os
import sys
import pytest

os.environ.setdefault("TCL_LIBRARY", r"C:\Users\Administrador\AppData\Local\Programs\Python\Python311\tcl\tcl8.6")
os.environ.setdefault("TK_LIBRARY", r"C:\Users\Administrador\AppData\Local\Programs\Python\Python311\tcl\tk8.6")

import tkinter as tk
from unittest.mock import MagicMock

def pytest_configure(config):
    try:
        root = tk.Tk()
        root.withdraw()
        root.destroy()
    except Exception:
        pass

@pytest.fixture(autouse=True)
def mock_tk_for_headless(monkeypatch):
    original_init = tk.Tk.__init__
    
    def mock_init(self):
        original_init(self)
        self.withdraw()
    
    try:
        monkeypatch.setattr(tk.Tk, "__init__", mock_init)
    except Exception:
        pass
