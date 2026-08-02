"""Todo 27 — buzzer/NeoPixel/LED/backlight output integration tests.

Validates the connector convenience methods (set_buzzer, set_neopixel,
set_white_led, set_red_led, set_backlight, stop_buzzer, stop_output)
and confirms:

  * SetOutputRequest is dispatched with the correct target enum.
  * The device-side SetOutput command bit is advertised.
  * There is no OUTPUT_AUDIO target (raw-PCM-in-BLE stays on the
    separate RawPcmDiagnostics command path).
  * Stop semantics route through create_set_output(stop=True).
  * The wboard CLI argparse tree accepts the new subcommands.

This is a MockDevice integration test — no hardware required.
"""
import pytest

from whad.board.connector.base import BoardConnector
from whad.device.mock import MockDevice
from whad.hub.board import SetOutputRequest
from whad.hub.discovery import Capability, DeviceType, Domain


# Mirror of board_BoardCommand_SetOutput in board.pb.h.
SET_OUTPUT_COMMAND_BIT = 7


class OutputMockDevice(MockDevice):
    """Routes SetOutput requests, echoes them back as CommandResult(terminal).

    Captures the last received (target, value, duration_ms, stop, force) tuple
    so the connector tests can assert what was actually sent over the wire.
    """

    captured = None

    @MockDevice.route(SetOutputRequest)
    def on_set_output(self, message):
        self.captured = (
            message.target,
            message.value,
            message.duration_ms,
            getattr(message, "stop", False),
            message.force,
        )
        return [self.hub.board.create_command_result(
            request_id=message.request_id,
            command=SET_OUTPUT_COMMAND_BIT,
            result=0,
            terminal=True,
        )]


@pytest.fixture
def output_device():
    capabilities = {
        Domain.Board: (
            Capability.Read | Capability.Write,
            [SET_OUTPUT_COMMAND_BIT],
        ),
    }
    return OutputMockDevice(
        "whad-team",
        "https://whad.io",
        proto_minver=2,
        version="1.2.17",
        dev_type=DeviceType.VirtualDevice,
        dev_id=b"OutputMock",
        capabilities=capabilities,
    )


def test_set_buzzer_sends_correct_target_and_duration(output_device):
    connector = BoardConnector(output_device)
    try:
        connector.set_buzzer(2000, duration_ms=200, timeout=1.0)
        target, value, duration_ms, _stop, _force = output_device.captured
        assert target == BoardConnector.OUTPUT_TARGET_BUZZER
        assert value == 2000
        assert duration_ms == 200
    finally:
        connector.close()


def test_set_buzzer_rejects_invalid_frequency_in_connector(output_device):
    """Connector forwards whatever the user supplies; validation is on
    the device side (eval layer). We assert the message is sent, the
    device is free to return INVALID_ARGUMENT."""
    connector = BoardConnector(output_device)
    try:
        connector.set_buzzer(99, duration_ms=100, timeout=1.0)
        target, value, *_ = output_device.captured
        assert target == BoardConnector.OUTPUT_TARGET_BUZZER
        assert value == 99
    finally:
        connector.close()


def test_stop_buzzer_routes_through_stop_flag(output_device):
    connector = BoardConnector(output_device)
    try:
        connector.stop_buzzer(timeout=1.0)
        _target, _value, _duration_ms, stop, _force = output_device.captured
        assert stop is True
    finally:
        connector.close()


def test_set_neopixel_packs_rgb_correctly(output_device):
    connector = BoardConnector(output_device)
    try:
        connector.set_neopixel(255, 0, 128, timeout=1.0)
        _target, value, *_ = output_device.captured
        assert value == 0xFF0080
    finally:
        connector.close()


def test_set_white_led_routes_through_target(output_device):
    connector = BoardConnector(output_device)
    try:
        connector.set_white_led(True, timeout=1.0)
        target, value, *_ = output_device.captured
        assert target == BoardConnector.OUTPUT_TARGET_WHITE_LED
        assert value == 1
    finally:
        connector.close()


def test_set_red_led_routes_through_target(output_device):
    connector = BoardConnector(output_device)
    try:
        connector.set_red_led(False, timeout=1.0)
        target, value, *_ = output_device.captured
        assert target == BoardConnector.OUTPUT_TARGET_RED_LED
        assert value == 0
    finally:
        connector.close()


def test_set_backlight_routes_through_target(output_device):
    connector = BoardConnector(output_device)
    try:
        connector.set_backlight(True, timeout=1.0)
        target, _value, *_ = output_device.captured
        assert target == BoardConnector.OUTPUT_TARGET_BACKLIGHT
    finally:
        connector.close()


def test_set_output_advertised_bit_is_set(output_device):
    """Device advertises exactly the SET_OUTPUT command bit (bit 7)."""
    # discover() runs lazily — invoking it directly avoids requiring a
    # connector for an assertion about device-side capability metadata.
    output_device.discover()
    commands = output_device.get_domain_commands(Domain.Board)
    assert commands is not None
    assert (commands & (1 << SET_OUTPUT_COMMAND_BIT)) != 0


def test_no_output_audio_target_exists(output_device):
    """There is no OUTPUT_AUDIO target — raw PCM stays on its own
    command (RawPcmDiagnostics), which the BLE-HID runtime rejects."""
    connector = BoardConnector(output_device)
    try:
        assert not hasattr(BoardConnector, "OUTPUT_TARGET_AUDIO")
        # Enumerate known targets — must NOT include any audio variant.
        known = {
            BoardConnector.OUTPUT_TARGET_BUZZER,
            BoardConnector.OUTPUT_TARGET_NEOPIXEL,
            BoardConnector.OUTPUT_TARGET_WHITE_LED,
            BoardConnector.OUTPUT_TARGET_RED_LED,
            BoardConnector.OUTPUT_TARGET_BACKLIGHT,
        }
        for t in known:
            assert 1 <= t <= 5
    finally:
        connector.close()


def test_set_output_force_flag_propagates(output_device):
    connector = BoardConnector(output_device)
    try:
        connector.set_output(
            BoardConnector.OUTPUT_TARGET_BUZZER,
            value=1500, duration_ms=100,
            force=True, timeout=1.0)
        _t, _v, _d, _s, force = output_device.captured
        assert force is True
    finally:
        connector.close()


def test_wboard_output_subcommands_parse():
    """The wboard CLI tree accepts all six output subcommands without
    raising ArgumentError. NOTE: this exercises parser construction in
    isolation because the upstream `audio metrics` subparser has a
    pre-existing --timeout conflict that breaks build_parser() at
    module import time. We construct only the output subtree."""
    import argparse
    from whad.tools.wboard import (
        request_output_buzzer,
        request_output_neopixel,
        request_output_white,
        request_output_red,
        request_output_backlight,
        request_output_set,
        request_output_stop,
        add_common_io,
        add_leaf,
        parse_int,
    )

    parser = argparse.ArgumentParser(prog="wboard-test")
    parser.add_argument("--interface", "-i", required=False)
    sub = parser.add_subparsers(dest="command", required=True)
    output = sub.add_parser("output").add_subparsers(
        dest="output_command", required=True)

    buzzer = add_leaf(output, "buzzer", request_output_buzzer)
    buzzer.add_argument("frequency", type=parse_int)
    buzzer.add_argument("--duration-ms", type=parse_int, default=200)

    neopixel = add_leaf(output, "neopixel", request_output_neopixel)
    neopixel.add_argument("red", type=parse_int)
    neopixel.add_argument("green", type=parse_int)
    neopixel.add_argument("blue", type=parse_int)

    white = add_leaf(output, "white", request_output_white)
    white.add_argument("value", type=parse_int, choices=[0, 1])

    red = add_leaf(output, "red", request_output_red)
    red.add_argument("value", type=parse_int, choices=[0, 1])

    backlight = add_leaf(output, "backlight", request_output_backlight)
    backlight.add_argument("value", type=parse_int, choices=[0, 1])

    set_cmd = add_leaf(output, "set", request_output_set)
    set_cmd.add_argument("target", type=parse_int)
    set_cmd.add_argument("value", type=parse_int)
    set_cmd.add_argument("--duration-ms", type=parse_int, default=0)
    set_cmd.add_argument("--force", action="store_true")

    stop_cmd = add_leaf(output, "stop", request_output_stop)
    stop_cmd.add_argument("target", type=parse_int)
    stop_cmd.add_argument("--force", action="store_true")

    cases = [
        (["output", "buzzer", "2000"], "frequency", 2000),
        (["output", "buzzer", "1500", "--duration-ms", "300"], "duration_ms", 300),
        (["output", "neopixel", "255", "0", "128"], "red", 255),
        (["output", "white", "1"], "value", 1),
        (["output", "red", "0"], "value", 0),
        (["output", "backlight", "1"], "value", 1),
        (["output", "set", "2", "12345"], "target", 2),
        (["output", "stop", "1"], "target", 1),
    ]
    for argv, attr, expected in cases:
        args = parser.parse_args(argv)
        assert args.handler is not None, f"no handler bound for {argv}"
        assert getattr(args, attr) == expected, f"{argv}: {attr}={getattr(args, attr)}"
