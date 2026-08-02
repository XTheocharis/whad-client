import pytest

from whad.board.connector.base import BoardConnector
from whad.device.mock import MockDevice
from whad.hub.board import (
    BoardCommandResult,
    CalibrateRequest,
    CalibrationResponse,
    Commands,
    ConfigureStreamRequest,
    ConfigureStreamResponse,
    GetBoardInfoRequest,
    GetCalibrationRequest,
    ListSensorsRequest,
    ListSensorsResponse,
    ReadSensorRequest,
    SensorSample,
    StopStreamRequest,
)
from whad.hub.discovery import Capability, DeviceType, Domain
from whad.protocol.board import board_pb2 as pb


MOTION_COMMANDS = [
    Commands.GetBoardInfo,
    Commands.GetRuntimeConfig,
    Commands.SetRuntimeConfig,
    Commands.SetRuntimeMode,
    Commands.ListSensors,
    Commands.ReadSensor,
    Commands.ConfigureStream,
    Commands.StopStream,
    Commands.Calibrate,
    Commands.GetCalibration,
]

MOTION_SENSORS = [
    (1, "acceleration", "mg", 3, 104000),
    (2, "gyroscope", "mdps", 3, 104000),
    (3, "magnetic", "milligauss", 3, 40000),
    (4, "quaternion", "q30", 4, 104000),
    (5, "orientation", "millidegrees", 3, 104000),
    (14, "air_mouse", "counts", 4, 60000),
]


def _clamp_rate(sensor_id, requested):
    for sid, _, _, _, max_rate in MOTION_SENSORS:
        if sid == sensor_id:
            return min(requested, max_rate) if requested > 0 else 0
    return 0


class MotionMockDevice(MockDevice):
    @MockDevice.route(GetBoardInfoRequest)
    def on_get_board_info(self, message):
        return self.hub.board.create_board_info_response(
            request_id=message.request_id,
            board_name="Adafruit CLUE",
            hardware_revision="nRF52840",
            firmware_version="1.0.0",
            protocol_variant="WHAD",
            device_id=b"\x01\x02\x03\x04",
            active_runtime=pb.RuntimeMode.RUNTIME_RAW_WHAD,
            implemented_sensor_count=6,
        )

    @MockDevice.route(ListSensorsRequest)
    def on_list_sensors(self, message):
        cursor = message.cursor
        if cursor >= len(MOTION_SENSORS):
            return self.hub.board.create(
                "sensor_descriptor",
                request_id=message.request_id,
                has_descriptor=False,
                next_cursor=cursor,
                eof=True,
            )
        sid, name, unit, vc, max_rate = MOTION_SENSORS[cursor]
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
            eof=(cursor + 1 >= len(MOTION_SENSORS)),
        )

    @MockDevice.route(ReadSensorRequest)
    def on_read_sensor(self, message):
        valid_ids = {s[0] for s in MOTION_SENSORS}
        if message.sensor_id not in valid_ids:
            return self.hub.board.create_command_result(
                request_id=message.request_id,
                command=pb.BoardCommand.ReadSensor,
                result=pb.BoardResultCode.SENSOR_FAULT,
                terminal=True,
                detail=b"",
            )
        return self.hub.board.create_sensor_sample(
            request_id=message.request_id,
            sensor_id=message.sensor_id,
            sequence=1,
            timestamp_us=1000,
            status=0,
            values=[10, 20, 30],
        )

    @MockDevice.route(ConfigureStreamRequest)
    def on_configure_stream(self, message):
        actual = _clamp_rate(message.sensor_id, message.rate_millihz)
        if actual == 0:
            return self.hub.board.create_command_result(
                request_id=message.request_id,
                command=pb.BoardCommand.ConfigureStream,
                result=pb.BoardResultCode.INVALID_ARGUMENT,
                terminal=True,
                detail=b"",
            )
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
            detail=b"",
        )

    @MockDevice.route(CalibrateRequest)
    def on_calibrate(self, message):
        return [
            self.hub.board.create_command_result(
                request_id=message.request_id,
                command=pb.BoardCommand.Calibrate,
                result=pb.BoardResultCode.SUCCESS,
                terminal=False,
                detail=b"accepted",
            ),
            self.hub.board.create_command_result(
                request_id=message.request_id,
                command=pb.BoardCommand.Calibrate,
                result=pb.BoardResultCode.SUCCESS,
                terminal=True,
                detail=b"done",
            ),
        ]

    @MockDevice.route(GetCalibrationRequest)
    def on_get_calibration(self, message):
        valid_ids = {s[0] for s in MOTION_SENSORS}
        if message.sensor_id not in valid_ids:
            return self.hub.board.create_command_result(
                request_id=message.request_id,
                command=pb.BoardCommand.GetCalibration,
                result=pb.BoardResultCode.SENSOR_FAULT,
                terminal=True,
                detail=b"",
            )
        return self.hub.board.create(
            "calibration",
            request_id=message.request_id,
            sensor_id=message.sensor_id,
            version=0,
            calibration_data=b"",
            persisted=False,
            crc32=0,
        )


@pytest.fixture
def motion_device():
    capabilities = {
        Domain.Board: (
            Capability.Read | Capability.Write | Capability.Stream,
            MOTION_COMMANDS,
        )
    }
    return MotionMockDevice(
        "whad-team",
        "https://whad.io",
        proto_minver=2,
        version="1.0.0",
        dev_type=DeviceType.VirtualDevice,
        dev_id=b"MotionMock",
        capabilities=capabilities,
    )


@pytest.fixture
def connector(motion_device):
    conn = BoardConnector(motion_device)
    yield conn
    conn.close()


def test_motion_commands_advertised(motion_device, connector):
    commands = motion_device.get_domain_commands(Domain.Board)

    assert commands & (1 << Commands.ListSensors) != 0
    assert commands & (1 << Commands.ReadSensor) != 0
    assert commands & (1 << Commands.ConfigureStream) != 0
    assert commands & (1 << Commands.StopStream) != 0
    assert commands & (1 << Commands.Calibrate) != 0
    assert commands & (1 << Commands.GetCalibration) != 0


def test_list_sensors_paginates_via_cursor(connector):
    resp0 = connector.list_sensors(cursor=0, timeout=3.0)
    assert isinstance(resp0, ListSensorsResponse)
    assert resp0.next_cursor == 1
    assert resp0.eof is False

    resp1 = connector.list_sensors(cursor=1, timeout=3.0)
    assert isinstance(resp1, ListSensorsResponse)
    assert resp1.next_cursor == 2
    assert resp1.eof is False


def test_list_sensors_eof_when_cursor_beyond_table(connector):
    resp = connector.list_sensors(cursor=99, timeout=3.0)

    assert isinstance(resp, ListSensorsResponse)
    assert resp.eof is True


def test_read_sensor_returns_sample_for_valid_id(connector):
    resp = connector.read_sensor(1, timeout=2.0)

    assert isinstance(resp, SensorSample)
    assert resp.sensor_id == 1
    assert resp.request_id != 0


def test_read_sensor_returns_fault_for_invalid_id(connector):
    resp = connector.read_sensor(99, timeout=2.0)

    assert isinstance(resp, BoardCommandResult)
    assert resp.result == pb.BoardResultCode.SENSOR_FAULT


def test_configure_stream_clamps_rate(connector):
    resp = connector.configure_stream(1, 999999, timeout=2.0)

    assert isinstance(resp, ConfigureStreamResponse)
    assert resp.sensor_id == 1
    assert resp.actual_rate_millihz == 104000


def test_configure_stream_rejects_invalid_sensor(connector):
    resp = connector.configure_stream(99, 50000, timeout=2.0)

    assert isinstance(resp, BoardCommandResult)
    assert resp.result == pb.BoardResultCode.INVALID_ARGUMENT


def test_stop_stream_is_idempotent(connector):
    resp1 = connector.stop_stream(1, timeout=2.0)
    resp2 = connector.stop_stream(1, timeout=2.0)

    assert isinstance(resp1, BoardCommandResult)
    assert resp1.result == pb.BoardResultCode.SUCCESS
    assert isinstance(resp2, BoardCommandResult)
    assert resp2.result == pb.BoardResultCode.SUCCESS


def test_calibrate_imu_returns_accepted_then_terminal(connector):
    resp = connector.calibrate_imu(timeout=2.0)

    assert isinstance(resp, BoardCommandResult)
    assert resp.terminal is True
    assert resp.result == pb.BoardResultCode.SUCCESS


def test_calibrate_mag_returns_success(connector):
    resp = connector.calibrate_mag(timeout=2.0)

    assert isinstance(resp, BoardCommandResult)
    assert resp.result == pb.BoardResultCode.SUCCESS


def test_get_calibration_returns_response_for_valid_sensor(connector):
    resp = connector.get_calibration(1, timeout=2.0)

    assert isinstance(resp, CalibrationResponse)
    assert resp.sensor_id == 1


def test_get_calibration_returns_fault_for_invalid_sensor(connector):
    resp = connector.get_calibration(99, timeout=2.0)

    assert isinstance(resp, BoardCommandResult)
    assert resp.result == pb.BoardResultCode.SENSOR_FAULT


def test_can_command_reflects_motion_commands(connector):
    assert connector.can_command(Commands.ListSensors) is True
    assert connector.can_command(Commands.ReadSensor) is True
    assert connector.can_command(Commands.Calibrate) is True
    assert connector.can_command(Commands.GetCalibration) is True
    assert connector.can_command(Commands.SetOutput) is False
