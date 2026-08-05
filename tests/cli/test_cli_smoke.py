"""Smoke tests for every whad-client CLI entry point.

Each test runs ``<tool> --help`` via :mod:`subprocess` and asserts the process
produces a usage banner identifying the tool. These are smoke tests only —
they verify the entry point is wired, imports cleanly, and the argparse parser
initializes; they do not exercise functionality.

Quirks tolerated by this module (pre-existing upstream behavior):

* ``winject --help`` exits ``1`` because ``WhadInjectApp.pre_run`` calls
  ``self.print_help()`` + ``sys.exit(1)`` before argparse gets the chance to
  handle ``--help`` natively. The help banner is still produced correctly,
  so we accept either exit 0 or 1 for ``winject``.
* ``wup`` is an alias of ``whadup`` and reuses its main, so its banner
  advertises ``whadup`` rather than ``wup``. We accept either name.
"""

from __future__ import annotations

import os
import shutil
import subprocess

import pytest

# (tool_name, needs_display, accepts_returncode_1, alias_names)
# ``alias_names`` lists additional names that may appear in the --help banner
# (e.g. ``wup`` is an alias of ``whadup``).
CLI_TOOLS: list[tuple[str, bool, bool, tuple[str, ...]]] = [
    ("whadup", False, False, ()),
    ("wup", False, False, ("whadup",)),  # alias of whadup
    ("wboard", False, False, ()),
    ("wanalyze", False, False, ()),
    ("wsniff", False, False, ()),
    # winject.pre_run() forces sys.exit(1) on --help (see module docstring).
    ("winject", False, True, ()),
    ("wshark", False, False, ()),
    ("wplay", False, False, ()),
    ("wdump", False, False, ()),
    ("wextract", False, False, ()),
    ("wfilter", False, False, ()),
    ("wserver", False, False, ()),
    ("winstall", False, False, ()),
    ("wzb-enddevice", False, False, ()),
    ("wble-central", False, False, ()),
    ("wble-clone", False, False, ()),
    ("wble-periph", False, False, ()),
    ("wble-connect", False, False, ()),
    ("wble-spawn", False, False, ()),
    ("wble-proxy", False, False, ()),
    ("wuni-scan", False, False, ()),
    # PyGame-based — may need a DISPLAY to import.
    ("wuni-mouse", True, False, ()),
    ("wuni-keyboard", True, False, ()),
    ("wreplay", False, False, ()),
]

_DISPLAY_AVAILABLE = bool(os.environ.get("DISPLAY"))


def _run_help(tool: str) -> subprocess.CompletedProcess[str]:
    """Run ``<tool> --help`` and return the completed process."""
    return subprocess.run(  # noqa: S603 — argv is fully controlled
        [tool, "--help"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )


def _make_test(tool: str, needs_display: bool, accepts_rc1: bool,
               aliases: tuple[str, ...]):
    """Build a smoke test for a single tool."""

    @pytest.mark.skipif(
        needs_display and not _DISPLAY_AVAILABLE,
        reason="PyGame-based tool requires a DISPLAY",
    )
    def test(self):
        if shutil.which(tool) is None:
            pytest.skip(f"{tool} not on PATH")
        result = _run_help(tool)

        acceptable_codes = {0, 1} if accepts_rc1 else {0}
        assert result.returncode in acceptable_codes, (
            f"{tool} --help exited {result.returncode} "
            f"(only {sorted(acceptable_codes)} accepted)\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )

        combined = result.stdout + result.stderr
        # A real --help banner advertises a "usage:" line. We require that
        # plus a self-identification (the tool name or one of its aliases).
        assert "usage" in combined.lower(), (
            f"{tool} did not print a usage banner:\n{combined}"
        )
        identity_names = (tool, *aliases)
        assert any(name in combined for name in identity_names), (
            f"none of {identity_names} appear in {tool} --help output:\n"
            f"{combined}"
        )

    return test


class TestCliSmoke:
    """One smoke test per CLI entry point."""

    pass


for _tool, _needs_display, _accepts_rc1, _aliases in CLI_TOOLS:
    setattr(
        TestCliSmoke,
        f"test_help_{_tool.replace('-', '_')}",
        _make_test(_tool, _needs_display, _accepts_rc1, _aliases),
    )
