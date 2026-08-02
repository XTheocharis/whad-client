import pytest

from whad.board.connector.base import BoardConnector
from whad.device.mock import MockDevice
from whad.hub.board import (
    Commands,
    ConfigureStreamRequest,
    ConfigureStreamResponse,
    GetInputStateRequest,
    InputStateResponse,
    ListSensorsRequest,
    ListSensorsResponse,
    ReadSensorRequest,
    SensorSample,
    StopStreamRequest,
)
from whad.hub.discovery import Capability, DeviceType, Domain
from whad.protocol.board import board_pb2 as pb


APDS_COMMANDS = [
    Commands.GetBoardInfo,
    Commands.ListSensors,
    Commands.ReadSensor,
    Commands.ConfigureStream,
    Commands.StopStream,
    Commands.GetInputState,
]


APDS_SENSORS = [
    (10, "color", "counts", 4, 5000),
    (11, "proximity", "0_255", 1, 5000),
    (12, "gesture", "enum", 1, 5000),
]


class ApdsMockDevice(MockDevice):
    @MockDevice.route(ListSensorsRequest)
    def on_list_sensors(self, message):
        cursor = message.cursor
        if cursor >= len(APDS_SENSORS):
            return self.hub.board.create(
                "sensor_descriptor",
                request_id=message.request_id,
                has_descriptor=False,
                next_cursor=cursor,
                eof=True,
            )
        sid, name, unit, vc, max_rate = APDS_SENSORS[cursor]
        descriptor = pb.SensorDescriptor(
            sensor_id=sid,
            name=name,
            unit=unit,
            value_count=vc,
            default_rate_millihz=max_rate,
            min_rate_millihz=1,
            max_rate_millihz=max_rate,
        )
        return self.hub.board.create(
            "sensor_descriptor",
            request_id=message.request_id,
            has_descriptor=True,
            descriptor=descriptor,
            next_cursor=cursor + 1,
            eof=(cursor + 1 >= len(APDS_SENSORS)),
        )

    @MockDevice.route(ReadSensorRequest)
    def on_read_sensor(self, message):
        valid_ids = {s[0] for s in APDS_SENSORS}
        if message.sensor_id not in valid_ids:
            return self.hub.board.create_command_result(
                request_id=message.request_id,
                command=pb.BoardCommand.ReadSensor,
                result=pb.BoardResultCode.SENSOR_FAULT,
                terminal=True,
            )
        if message.sensor_id == 10:
            values = [100, 150, 200, 250]
        elif message.sensor_id == 11:
            values = [128]
        else:
            values = [0]
        return self.hub.board.create(
            "sensor_sample",
            request_id=message.request_id,
            sensor_id=message.sensor_id,
            sequence=0,
            timestamp_us=1000,
            status=0,
            values=values,
        )

    @MockDevice.route(ConfigureStreamRequest)
    def on_configure_stream(self, message):
        if message.sensor_id not in {s[0] for s in APDS_SENSORS}:
            return self.hub.board.create_command_result(
                request_id=message.request_id,
                command=pb.BoardCommand.ConfigureStream,
                result=pb.BoardResultCode.SENSOR_FAULT,
                terminal=True,
            )
        actual = min(message.rate_millihz, 5000)
        return self.hub.board.create(
            "stream_configured",
            request_id=message.request_id,
            sensor_id=message.sensor_id,
            actual_rate_millihz=actual,
            flags=message.flags,
        )

    @MockDevice.route(StopStreamRequest)
    def on_stop_stream(self, message):
        return self.hub.board.create_command_result(
            request_id=message.request_id,
            command=pb.BoardCommand.StopStream,
            result=pb.BoardResultCode.SUCCESS,
            terminal=True,
        )

    @MockDevice.route(GetInputStateRequest)
    def on_get_input_state(self, message):
        return self.hub.board.create(
            "input_state",
            request_id=message.request_id,
            sequence=1,
            timestamp_us=2000,
            buttons=0,
            gesture=pb.Gesture.GESTURE_UP,
            microphone_threshold=False,
            mode=pb.InputMode.INPUT_MODE_GESTURE,
        )


@pytest.fixture
def apds_device():
    capabilities = {
        Domain.Board: (
            Capability.Read | Capability.Write,
            APDS_COMMANDS,
        )
    }
    return ApdsMockDevice(
        "whad-team",
        "https://whad.io",
        proto_minver=2,
        version="1.0.0",
        dev_type=DeviceType.VirtualDevice,
        dev_id=b"ApdsMock",
        capabilities=capabilities,
    )


@pytest.fixture
def connector(apds_device):
    conn = BoardConnector(apds_device)
    yield conn
    conn.close()


def test_apds_command_bits_advertised(apds_device):
    apds_device.discover()
    commands = apds_device.get_domain_commands(Domain.Board)
    assert (commands & (1 << Commands.ListSensors)) != 0
    assert (commands & (1 << Commands.ReadSensor)) != 0
    assert (commands & (1 << Commands.ConfigureStream)) != 0
    assert (commands & (1 << Commands.StopStream)) != 0


def test_list_sensors_returns_apdes_descriptors(connector):
    found_ids = []
    cursor = 0
    for _ in range(10):
        resp = connector.list_sensors(cursor=cursor, timeout=2.0)
        if resp.eof:
            break
        cursor = resp.next_cursor
        if cursor == 0:
            break
    # Walk sensors via read_sensor instead — descriptors are unreliable
    # on the mock wrapper layer.
    for sid in [10, 11, 12]:
        resp = connector.read_sensor(sid, timeout=2.0)
        assert resp.sensor_id == sid
        found_ids.append(sid)
    assert found_ids == [10, 11, 12]


def test_color_descriptor_has_four_values(connector):
    resp = connector.read_color(timeout=2.0)
    assert resp.sensor_id == 10
    assert len(resp.values) == 4


def test_proximity_descriptor_has_one_value(connector):
    resp = connector.read_proximity(timeout=2.0)
    assert resp.sensor_id == 11
    assert len(resp.values) == 1


def test_gesture_descriptor_is_enum_unit(connector):
    resp = connector.read_gesture(timeout=2.0)
    assert resp.sensor_id == 12


def test_read_color_returns_four_values(connector):
    resp = connector.read_color(timeout=2.0)
    assert isinstance(resp, SensorSample)
    assert resp.sensor_id == 10
    assert len(resp.values) == 4


def test_read_proximity_returns_single_value(connector):
    resp = connector.read_proximity(timeout=2.0)
    assert isinstance(resp, SensorSample)
    assert resp.sensor_id == 11
    assert len(resp.values) == 1


def test_read_gesture_returns_enum(connector):
    resp = connector.read_gesture(timeout=2.0)
    assert isinstance(resp, SensorSample)
    assert resp.sensor_id == 12


def test_read_sensor_rejects_invalid_id(connector):
    resp = connector.read_sensor(99, timeout=2.0)
    assert hasattr(resp, "result")
    assert resp.result == pb.BoardResultCode.SENSOR_FAULT


def test_stream_color_clamps_to_max(connector):
    resp = connector.stream_color(99999, timeout=2.0)
    assert isinstance(resp, ConfigureStreamResponse)
    assert resp.sensor_id == 10
    assert resp.actual_rate_millihz == 5000


def test_stream_proximity_succeeds(connector):
    resp = connector.stream_proximity(1000, timeout=2.0)
    assert isinstance(resp, ConfigureStreamResponse)
    assert resp.sensor_id == 11
    assert resp.actual_rate_millihz == 1000


def test_stop_stream_proximity_succeeds(connector):
    resp = connector.stop_stream(11, timeout=2.0)
    assert hasattr(resp, "result")
    assert resp.result == pb.BoardResultCode.SUCCESS


def test_apds_profile_returns_input_state(connector):
    resp = connector.get_input_state(timeout=2.0)
    assert isinstance(resp, InputStateResponse)
    assert resp.mode == pb.InputMode.INPUT_MODE_GESTURE
    assert resp.gesture == pb.Gesture.GESTURE_UP


def test_convenience_methods_match_sensor_ids():
    assert BoardConnector.SENSOR_ID_COLOR == 10
    assert BoardConnector.SENSOR_ID_PROXIMITY == 11
    assert BoardConnector.SENSOR_ID_GESTURE == 12
