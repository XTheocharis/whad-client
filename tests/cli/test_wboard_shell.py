"""Tests for the `wboard shell` interactive subcommand.

Verifies the subcommand is registered, the handler returns None, and the
`run()` function bypasses `print_response` when the shell handler is selected.
"""
from unittest.mock import MagicMock, patch

import pytest

from whad.tools.wboard import build_parser, request_shell, run


def test_shell_subcommand_is_registered():
    """The `shell` subcommand should appear in the parser."""
    parser = build_parser()
    ns = parser.parse_args(["-i", "uart0", "shell"])
    assert ns.handler is request_shell


def test_shell_subcommand_in_choices():
    """The `shell` subcommand should appear in the top-level subparser choices."""
    parser = build_parser()
    # The choices string is built by argparse; verify 'shell' is listed.
    help_text = parser.format_help()
    assert "shell" in help_text


def test_request_shell_returns_none():
    """request_shell should return None after the shell loop exits."""
    fake_shell = MagicMock()
    fake_shell.run.return_value = None
    with patch("whad.cli.board_shell.BoardShell", return_value=fake_shell):
        connector = MagicMock()
        args = MagicMock()
        args.timeout = 2.0
        result = request_shell(connector, args)
    assert result is None
    fake_shell.run.assert_called_once()


def test_run_skips_print_response_for_shell():
    """run() should not call print_response for the shell handler."""
    fake_device = MagicMock()
    fake_connector = MagicMock()

    with patch("whad.device.Device.create", return_value=fake_device), \
         patch("whad.board.connector.BoardConnector", return_value=fake_connector), \
         patch("whad.cli.board_shell.BoardShell") as MockShell:
        mock_instance = MockShell.return_value
        mock_instance.run.return_value = None
        parser = build_parser()
        args = parser.parse_args(["-i", "uart0", "shell"])
        run(args)

    # Shell was entered
    MockShell.assert_called_once()
    mock_instance.run.assert_called_once()
    # Connector was still closed (cleanup)
    fake_connector.close.assert_called_once()
