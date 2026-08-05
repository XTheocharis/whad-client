"""Smoke tests: every scapy layer submodule imports cleanly.

Catches syntax errors, missing deps, and broken imports without
exercising packet dissection. scapy has 17 .py files and previously
had zero dedicated test coverage.
"""
import importlib

import pytest

# Dotted module paths for every file under whad/scapy/ (17 modules).
SCAPY_MODULES = [
    "whad.scapy",
    "whad.scapy.layers",
    "whad.scapy.layers.apimote",
    "whad.scapy.layers.bluetooth",
    "whad.scapy.layers.bt_mesh",
    "whad.scapy.layers.dot15d4tap",
    "whad.scapy.layers.esb",
    "whad.scapy.layers.hci",
    "whad.scapy.layers.lorawan",
    "whad.scapy.layers.microsoft",
    "whad.scapy.layers.nordic",
    "whad.scapy.layers.phy",
    "whad.scapy.layers.rf4ce",
    "whad.scapy.layers.ubertooth",
    "whad.scapy.layers.unifying",
    "whad.scapy.layers.zdp",
    "whad.scapy.layers.zll",
]


@pytest.mark.parametrize("module_name", SCAPY_MODULES)
def test_scapy_module_imports(module_name: str) -> None:
    try:
        importlib.import_module(module_name)
    except ImportError as exc:
        pytest.fail(f"Failed to import {module_name}: {exc}")
