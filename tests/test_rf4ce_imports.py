"""Smoke tests: every rf4ce submodule imports cleanly.

Catches syntax errors, missing deps, and broken imports without
exercising protocol behaviour. rf4ce has 28 .py files and previously
had zero dedicated test coverage.
"""
import importlib

import pytest

# Dotted module paths for every file under whad/rf4ce/ (28 modules).
RF4CE_MODULES = [
    "whad.rf4ce",
    "whad.rf4ce.connector",
    "whad.rf4ce.connector.base",
    "whad.rf4ce.connector.controller",
    "whad.rf4ce.connector.injector",
    "whad.rf4ce.connector.sniffer",
    "whad.rf4ce.connector.target",
    "whad.rf4ce.crypto",
    "whad.rf4ce.exceptions",
    "whad.rf4ce.injecting",
    "whad.rf4ce.sniffing",
    "whad.rf4ce.stack.apl",
    "whad.rf4ce.stack.apl.database",
    "whad.rf4ce.stack.apl.exceptions",
    "whad.rf4ce.stack.apl.profile",
    "whad.rf4ce.stack.apl.profiles",
    "whad.rf4ce.stack.apl.profiles.mso",
    "whad.rf4ce.stack.apl.profiles.mso.database",
    "whad.rf4ce.stack.apl.profiles.mso.parsers",
    "whad.rf4ce.stack.apl.profiles.zrc",
    "whad.rf4ce.stack.nwk",
    "whad.rf4ce.stack.nwk.database",
    "whad.rf4ce.stack.nwk.exceptions",
    "whad.rf4ce.stack.nwk.pairing",
    "whad.rf4ce.utils",
    "whad.rf4ce.utils.adpcm",
    "whad.rf4ce.utils.analyzer",
    "whad.rf4ce.utils.phy",
]


@pytest.mark.parametrize("module_name", RF4CE_MODULES)
def test_rf4ce_module_imports(module_name: str) -> None:
    try:
        importlib.import_module(module_name)
    except ImportError as exc:
        pytest.fail(f"Failed to import {module_name}: {exc}")
