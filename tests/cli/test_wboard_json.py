"""Tests for the `wboard --json` output mode.

The `--json` flag was previously registered (via ``add_common_io``) but never
honored — ``print_response`` ignored its presence and always emitted the
Python ``repr()`` of the response wrapper. These tests exercise both the JSON
code path and the unchanged default path.
"""
import json
from unittest.mock import MagicMock, patch

import pytest

from whad.hub.board import BoardInfoResponse
from whad.protocol.whad_pb2 import Message
from whad.tools.wboard import build_parser, print_response, run


def _make_board_info_response() -> BoardInfoResponse:
    """Build a canned ``BoardInfoResponse`` fixture (no live device required)."""
    msg = Message()
    msg.board.request_id = 1
    msg.board.board_info.board_name = "Adafruit CLUE"
    msg.board.board_info.hardware_revision = "rev-a"
    msg.board.board_info.firmware_version = "1.1.5"
    msg.board.board_info.protocol_variant = "board-v1"
    msg.board.board_info.device_id = b"CLUE"
    msg.board.board_info.active_runtime = 1
    msg.board.board_info.implemented_sensor_count = 14
    return BoardInfoResponse(message=msg)


def _run_wboard(argv, capsys):
    """Drive ``wboard.run`` with a mocked ``BoardConnector``.

    Patches happen at the import source so the lazy ``from whad.board.connector
    import BoardConnector`` inside :func:`run` resolves to the mock.
    """
    response = _make_board_info_response()
    parser = build_parser()
    args = parser.parse_args(argv)

    mock_connector = MagicMock()
    mock_connector.get_board_info.return_value = response
    with patch("whad.board.connector.BoardConnector", return_value=mock_connector), \
         patch("whad.device.Device.create", return_value=MagicMock()):
        run(args)
    return capsys.readouterr().out


# ---------------------------------------------------------------------------
# Unit-level: print_response directly
# ---------------------------------------------------------------------------

def test_print_response_json_mode_outputs_valid_json(capsys):
    """Given ``json_mode=True``, ``print_response`` writes parseable JSON."""
    response = _make_board_info_response()
    print_response(response, json_mode=True)
    out = capsys.readouterr().out

    parsed = json.loads(out)
    assert isinstance(parsed, dict)
    # The wrapper.message is a top-level whad Message; the board_info lives
    # under the board oneof.
    assert parsed["board"]["board_info"]["board_name"] == "Adafruit CLUE"
    assert parsed["board"]["board_info"]["implemented_sensor_count"] == 14


def test_print_response_default_mode_outputs_repr(capsys):
    """Given ``json_mode=False`` (default), output is the wrapper repr — not JSON."""
    response = _make_board_info_response()
    print_response(response)
    out = capsys.readouterr().out

    with pytest.raises(json.JSONDecodeError):
        json.loads(out)
    assert "BoardInfoResponse" in out


def test_print_response_none_is_noop(capsys):
    """Handlers returning ``None`` (e.g. ``audio metrics``) must not crash."""
    print_response(None, json_mode=True)
    print_response(None, json_mode=False)
    assert capsys.readouterr().out == ""


# ---------------------------------------------------------------------------
# Integration-level: run() dispatches args.json correctly
# ---------------------------------------------------------------------------

def test_run_emits_json_with_flag(capsys):
    """`wboard -i uart0 info --json` produces JSON-parseable stdout."""
    out = _run_wboard(["-i", "uart0", "info", "--json"], capsys)
    parsed = json.loads(out)
    assert parsed["board"]["board_info"]["board_name"] == "Adafruit CLUE"


def test_run_emits_repr_without_flag(capsys):
    """`wboard -i uart0 info` (no --json) produces the original Python repr."""
    out = _run_wboard(["-i", "uart0", "info"], capsys)
    with pytest.raises(json.JSONDecodeError):
        json.loads(out)
    assert "BoardInfoResponse" in out
    # Belt-and-braces: default output never starts a JSON object/array.
    assert not out.lstrip().startswith(("{", "["))


def test_run_json_flag_is_the_only_trigger(capsys):
    """Same fixture, two invocations — JSON only when ``--json`` is present."""
    json_out = _run_wboard(["-i", "uart0", "info", "--json"], capsys)
    repr_out = _run_wboard(["-i", "uart0", "info"], capsys)

    json.loads(json_out)  # must parse
    with pytest.raises(json.JSONDecodeError):
        json.loads(repr_out)
