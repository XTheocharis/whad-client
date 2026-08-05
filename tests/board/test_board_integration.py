import pytest

from whad.board.connector.base import BoardConnector
from whad.device.mock import MockDevice
from whad.hub.board import (
    BoardCommandResult,
    BoardInfoResponse,
    BoardStatus,
    Commands,
    ConfigureInputRequest,
    GetBoardInfoRequest,
    GetInputStateRequest,
    GetRuntimeConfigRequest,
    InputStateResponse,
    RemoteProfileGetRequest,
    RemoteProfileResponse,
    RuntimeConfigResponse,
    SetRuntimeConfigRequest,
    SetRuntimeModeRequest,
    StorageInfoRequest,
    ListSensorsRequest,
    ReadSensorRequest,
    ConfigureStreamRequest,
    StopStreamRequest,
    CalibrateRequest,
    GetCalibrationRequest,
    SetOutputRequest,
    AudioConfigureRequest,
    I2cTransferRequest,
    SpiTransferRequest,
    ReleasePinRequest,
    RawPcmDiagnosticsRequest,
)
from whad.hub.discovery import Capability, DeviceType, Domain
from whad.protocol.board import board_pb2 as pb


IMPL_COMMANDS = [
    Commands.GetBoardInfo,
    Commands.GetRuntimeConfig,
    Commands.SetRuntimeConfig,
    Commands.SetRuntimeMode,
    Commands.GetInputState,
    Commands.ConfigureInput,
    Commands.RemoteProfileGet,
    Commands.RemoteProfileSet,
    Commands.ListSensors,
    Commands.ReadSensor,
    Commands.ConfigureStream,
    Commands.StopStream,
    Commands.Calibrate,
    Commands.GetCalibration,
    Commands.SetOutput,
    Commands.AudioConfigure,
    Commands.I2cTransfer,
    Commands.SpiTransfer,
    Commands.ReleasePin,
    Commands.RawPcmDiagnostics,
]
assert len(IMPL_COMMANDS) == 20


class ClueMockDevice(MockDevice):
    """Mock device emulating the CLUE Board domain firmware.

    Implements the same 4 handlers as BoardModule (Wave 2) and returns
    NOT_IMPLEMENTED for everything else.
    """

    @MockDevice.route(GetBoardInfoRequest)
    def on_get_board_info(self, message):
        return self.hub.board.create_board_info_response(
            request_id=message.request_id,
            board_name="Adafruit CLUE",
            hardware_revision="nRF52840",
            firmware_version="1.0.0",
            protocol_variant="WHAD",
            device_id=b"\x01\x02\x03\x04\x05\x06\x07\x08",
            active_runtime=pb.RuntimeMode.RUNTIME_RAW_WHAD,
            implemented_sensor_count=0,
        )

    @MockDevice.route(GetRuntimeConfigRequest)
    def on_get_runtime_config(self, message):
        return self.hub.board.create(
            "runtime_config",
            request_id=message.request_id,
            active_runtime=pb.RuntimeMode.RUNTIME_RAW_WHAD,
            persisted_runtime=pb.RuntimeMode.RUNTIME_UNKNOWN,
            persistence_available=False,
            ble_advertising=False,
            ble_pairable=False,
            ble_connected=False,
            bond_count=0,
            event_log_filter=0,
            raw_packet_log_filter=0,
        )

    @MockDevice.route(SetRuntimeModeRequest)
    def on_set_runtime_mode(self, message):
        if message.runtime == pb.RuntimeMode.RUNTIME_UNKNOWN:
            code = pb.BoardResultCode.WRONG_MODE
        elif message.persist:
            code = pb.BoardResultCode.NOT_ADOPTED
        else:
            code = pb.BoardResultCode.SUCCESS
        return self.hub.board.create_command_result(
            request_id=message.request_id,
            command=pb.BoardCommand.SetRuntimeMode,
            result=code,
            terminal=True,
            detail=b"",
        )

    @MockDevice.route(SetRuntimeConfigRequest)
    def on_set_runtime_config(self, message):
        op = message.message.board.set_runtime_config.WhichOneof("operation")
        result = pb.BoardResultCode.SUCCESS
        if op == "update":
            if message.message.board.set_runtime_config.update.has_persisted_runtime:
                result = pb.BoardResultCode.NOT_ADOPTED
        return self.hub.board.create_command_result(
            request_id=message.request_id,
            command=pb.BoardCommand.SetRuntimeConfig,
            result=result,
            terminal=True,
            detail=b"",
        )

    @MockDevice.route(GetInputStateRequest)
    def on_get_input_state(self, message):
        return self.hub.board.create(
            "input_state",
            request_id=message.request_id,
            sequence=1,
            timestamp_us=1000,
            buttons=0,
            gesture=pb.Gesture.GESTURE_UNKNOWN,
            microphone_threshold=False,
            mode=pb.InputMode.INPUT_MODE_REMOTE,
        )

    @MockDevice.route(RemoteProfileGetRequest)
    def on_remote_profile_get(self, message):
        resp = self.hub.board.create(
            "remote_profile",
            request_id=message.request_id,
        )
        profile = resp.message.board.remote_profile.profile
        profile.profile_id = message.profile_id
        profile.name = "android_tv"
        profile.sensitivity = 10
        profile.deadzone = 800
        profile.pointer_mode = False
        profile.tilt_mode = False
        return resp

    @MockDevice.route(ConfigureInputRequest)
    def on_configure_input(self, message):
        code = pb.BoardResultCode.SUCCESS
        if message.mode == pb.InputMode.INPUT_MODE_UNKNOWN:
            code = pb.BoardResultCode.INVALID_ARGUMENT
        elif message.persist:
            code = pb.BoardResultCode.NOT_ADOPTED
        return self.hub.board.create_command_result(
            request_id=message.request_id,
            command=pb.BoardCommand.ConfigureInput,
            result=code,
            terminal=True,
            detail=b"",
        )

    @MockDevice.route(StorageInfoRequest)
    def on_storage_info(self, message):
        return self.hub.board.create_command_result(
            request_id=message.request_id,
            command=pb.BoardCommand.StorageInfo,
            result=pb.BoardResultCode.NOT_IMPLEMENTED,
            terminal=True,
            detail=b"",
        )

    @MockDevice.route(ListSensorsRequest)
    def on_list_sensors(self, message):
        return self.hub.board.create(
            "list_sensors",
            request_id=message.request_id,
            sensor_count=14,
            next_cursor=0,
        )

    @MockDevice.route(ReadSensorRequest)
    def on_read_sensor(self, message):
        return self.hub.board.create_command_result(
            request_id=message.request_id,
            command=pb.BoardCommand.ReadSensor,
            result=pb.BoardResultCode.SUCCESS,
            terminal=True,
            detail=b"",
        )

    @MockDevice.route(ConfigureStreamRequest)
    def on_configure_stream(self, message):
        return self.hub.board.create_command_result(
            request_id=message.request_id,
            command=pb.BoardCommand.ConfigureStream,
            result=pb.BoardResultCode.SUCCESS,
            terminal=True,
            detail=b"",
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
        return self.hub.board.create_command_result(
            request_id=message.request_id,
            command=pb.BoardCommand.Calibrate,
            result=pb.BoardResultCode.SUCCESS,
            terminal=True,
            detail=b"",
        )

    @MockDevice.route(GetCalibrationRequest)
    def on_get_calibration(self, message):
        return self.hub.board.create(
            "calibration",
            request_id=message.request_id,
            sensor_id=message.sensor_id,
        )

    @MockDevice.route(SetOutputRequest)
    def on_set_output(self, message):
        return self.hub.board.create_command_result(
            request_id=message.request_id,
            command=pb.BoardCommand.SetOutput,
            result=pb.BoardResultCode.SUCCESS,
            terminal=True,
            detail=b"",
        )

    @MockDevice.route(AudioConfigureRequest)
    def on_audio_configure(self, message):
        return self.hub.board.create(
            "audio_configure",
            request_id=message.request_id,
            enabled=message.enabled,
        )

    @MockDevice.route(I2cTransferRequest)
    def on_i2c_transfer(self, message):
        return self.hub.board.create(
            "i2c_transfer",
            request_id=message.request_id,
            read_data=b"\x00" * message.read_length,
        )

    @MockDevice.route(SpiTransferRequest)
    def on_spi_transfer(self, message):
        return self.hub.board.create(
            "spi_transfer",
            request_id=message.request_id,
            read_data=b"\x00" * message.read_length,
        )

    @MockDevice.route(ReleasePinRequest)
    def on_release_pin(self, message):
        return self.hub.board.create_command_result(
            request_id=message.request_id,
            command=pb.BoardCommand.ReleasePin,
            result=pb.BoardResultCode.SUCCESS,
            terminal=True,
            detail=b"",
        )

    @MockDevice.route(RawPcmDiagnosticsRequest)
    def on_raw_pcm_diagnostics(self, message):
        return self.hub.board.create_command_result(
            request_id=message.request_id,
            command=pb.BoardCommand.RawPcmDiagnostics,
            result=pb.BoardResultCode.SUCCESS,
            terminal=True,
            detail=b"",
        )


@pytest.fixture
def clue_device():
    capabilities = {
        Domain.Board: (
            Capability.Read | Capability.Write,
            IMPL_COMMANDS,
        )
    }
    return ClueMockDevice(
        "whad-team",
        "https://whad.io",
        proto_minver=2,
        version="1.0.0",
        dev_type=DeviceType.VirtualDevice,
        dev_id=b"ClueMock",
        capabilities=capabilities,
    )


@pytest.fixture
def connector(clue_device):
    conn = BoardConnector(clue_device)
    yield conn
    conn.close()


def test_get_board_info_returns_correlated_response(connector):
    response = connector.get_board_info(timeout=2.0)

    assert isinstance(response, BoardInfoResponse)
    assert response.board_name == "Adafruit CLUE"
    assert response.firmware_version == "1.0.0"
    assert response.active_runtime == pb.RuntimeMode.RUNTIME_RAW_WHAD
    assert response.implemented_sensor_count == 0
    assert response.request_id != 0


def test_sensor_command_bits_present(clue_device, connector):
    clue_device.discover()
    commands = clue_device.get_domain_commands(Domain.Board)

    assert (commands & (1 << Commands.ListSensors)) != 0
    assert (commands & (1 << Commands.ReadSensor)) != 0
    assert (commands & (1 << Commands.AudioConfigure)) != 0
    assert (commands & (1 << Commands.I2cTransfer)) != 0
    assert (commands & (1 << Commands.SpiTransfer)) != 0

    assert (commands & (1 << Commands.StorageInfo)) == 0
    assert (commands & (1 << Commands.GpioConfigure)) == 0
    assert (commands & (1 << Commands.AdcRead)) == 0

    assert (commands & (1 << Commands.GetBoardInfo)) != 0
    assert (commands & (1 << Commands.GetRuntimeConfig)) != 0
    assert (commands & (1 << Commands.SetRuntimeMode)) != 0
    assert (commands & (1 << Commands.SetRuntimeConfig)) != 0


def test_unsupported_request_returns_not_implemented(connector):
    msg = connector.hub.board.create_storage_info()
    response = connector.send_request(msg, timeout=2.0)

    assert isinstance(response, BoardCommandResult)
    assert response.result == pb.BoardResultCode.NOT_IMPLEMENTED
    assert response.terminal is True
    assert response.command == pb.BoardCommand.StorageInfo


def test_get_runtime_config_returns_correlated_response(connector):
    msg = connector.hub.board.create_get_runtime_config()
    response = connector.send_request(msg, timeout=2.0)

    assert isinstance(response, RuntimeConfigResponse)
    assert response.active_runtime == pb.RuntimeMode.RUNTIME_RAW_WHAD
    assert response.persisted_runtime == pb.RuntimeMode.RUNTIME_UNKNOWN
    assert response.persistence_available is False
    assert response.bond_count == 0
    assert response.request_id != 0


def test_set_runtime_mode_success_correlated(connector):
    msg = connector.hub.board.create_set_runtime_mode(
        runtime=pb.RuntimeMode.RUNTIME_BLE_HID,
        persist=False,
        reboot=False,
    )
    response = connector.send_request(msg, timeout=2.0)

    assert isinstance(response, BoardCommandResult)
    assert response.result == pb.BoardResultCode.SUCCESS
    assert response.command == pb.BoardCommand.SetRuntimeMode
    assert response.terminal is True


def test_set_runtime_mode_wrong_mode_correlated(connector):
    msg = connector.hub.board.create_set_runtime_mode(
        runtime=pb.RuntimeMode.RUNTIME_UNKNOWN,
        persist=False,
        reboot=False,
    )
    response = connector.send_request(msg, timeout=2.0)

    assert isinstance(response, BoardCommandResult)
    assert response.result == pb.BoardResultCode.WRONG_MODE


def test_set_runtime_config_success_correlated(connector):
    msg = connector.hub.board.create(
        "set_runtime_config",
        request_id=0,
    )
    response = connector.send_request(msg, timeout=2.0)

    assert isinstance(response, BoardCommandResult)
    assert response.result == pb.BoardResultCode.SUCCESS
    assert response.command == pb.BoardCommand.SetRuntimeConfig


def test_request_ids_correlate_across_round_trips(connector):
    r1 = connector.get_board_info(timeout=2.0)
    r2 = connector.send_request(
        connector.hub.board.create_get_runtime_config(),
        timeout=2.0,
    )

    assert r1.request_id != r2.request_id
    assert r1.request_id != 0
    assert r2.request_id != 0


def test_connector_can_command_only_advertised(connector):
    assert connector.can_command(Commands.GetBoardInfo) is True
    assert connector.can_command(Commands.SetRuntimeMode) is True
    assert connector.can_command(Commands.ListSensors) is True
    assert connector.can_command(Commands.AudioConfigure) is True
    assert connector.can_command(Commands.StorageInfo) is False
    assert connector.can_command(Commands.GpioConfigure) is False


def test_get_input_state_returns_correlated_response(connector):
    response = connector.get_input_state(timeout=2.0)

    assert isinstance(response, InputStateResponse)
    assert response.request_id != 0
    assert response.mode == pb.InputMode.INPUT_MODE_REMOTE


def test_configure_input_success_correlated(connector):
    response = connector.configure_input(
        mode=pb.InputMode.INPUT_MODE_GESTURE,
        dwell_ms=500,
        timeout=2.0,
    )

    assert isinstance(response, BoardCommandResult)
    assert response.result == pb.BoardResultCode.SUCCESS
    assert response.command == pb.BoardCommand.ConfigureInput


def test_remote_profile_get_returns_correlated_response(connector):
    response = connector.remote_profile_get(profile_id=0, timeout=2.0)

    assert isinstance(response, RemoteProfileResponse)
    assert response.request_id != 0
    raw = response.message.board.remote_profile
    assert raw.profile.name == "android_tv"
    assert raw.profile.sensitivity == 10


def test_start_pairing_sends_open_pairing_window(connector):
    response = connector.start_pairing(duration_ms=60000, timeout=2.0)

    assert isinstance(response, BoardCommandResult)
    assert response.result == pb.BoardResultCode.SUCCESS
    assert response.command == pb.BoardCommand.SetRuntimeConfig


def test_forget_bonds_sends_clear_bonds(connector):
    response = connector.forget_bonds(confirm_nonce=12345, timeout=2.0)

    assert isinstance(response, BoardCommandResult)
    assert response.result == pb.BoardResultCode.SUCCESS
    assert response.command == pb.BoardCommand.SetRuntimeConfig


def test_input_and_profile_command_bits_advertised(clue_device):
    clue_device.discover()
    commands = clue_device.get_domain_commands(Domain.Board)

    assert (commands & (1 << Commands.GetInputState)) != 0
    assert (commands & (1 << Commands.ConfigureInput)) != 0
    assert (commands & (1 << Commands.RemoteProfileGet)) != 0
    assert (commands & (1 << Commands.RemoteProfileSet)) != 0


class ClueWithEventMockDevice(ClueMockDevice):
    """Emits an interleaved BoardStatus event (zero request_id)
    before the terminal response for GetBoardInfo."""

    @MockDevice.route(GetBoardInfoRequest)
    def on_get_board_info(self, message):
        event = self.hub.board.create(
            "board_status",
            request_id=0,
            sequence=1,
            timestamp_us=42,
            status=pb.BoardStatusCode.BOARD_STATUS_UNKNOWN,
            detail=b"running",
            terminal=False,
        )
        response = self.hub.board.create_board_info_response(
            request_id=message.request_id,
            board_name="Adafruit CLUE",
            hardware_revision="nRF52840",
            firmware_version="1.0.0",
            protocol_variant="WHAD",
            device_id=b"\x00",
            active_runtime=pb.RuntimeMode.RUNTIME_RAW_WHAD,
            implemented_sensor_count=0,
        )
        return [event, response]


@pytest.fixture
def event_device():
    capabilities = {
        Domain.Board: (
            Capability.Read | Capability.Write,
            IMPL_COMMANDS,
        )
    }
    return ClueWithEventMockDevice(
        "whad-team",
        "https://whad.io",
        proto_minver=2,
        version="1.0.0",
        dev_type=DeviceType.VirtualDevice,
        dev_id=b"ClueEventMock",
        capabilities=capabilities,
    )


def test_interleaved_status_event_separated_from_response(event_device):
    conn = BoardConnector(event_device)
    try:
        response = conn.get_board_info(timeout=2.0)
        event = conn.next_event(timeout=2.0)

        assert isinstance(response, BoardInfoResponse)
        assert response.request_id != 0
        assert response.board_name == "Adafruit CLUE"

        assert isinstance(event, BoardStatus)
        assert event.request_id == 0
    finally:
        conn.close()
