from whad.hub.message import PbFieldBool, PbFieldBytes, PbFieldInt, PbFieldMsg
from whad.protocol.board import board_pb2 as pb

from .common import BoardMessage
from .domain import BoardDomain
from ..message import pb_bind


class SensorDescriptor:
    """Wrapper exposing the raw protobuf ``SensorDescriptor`` fields.

    ``PbFieldMsg`` calls ``wrap_class(pb_message)`` on read, so we forward
    attribute access to the underlying protobuf message.
    """

    def __init__(self, message):
        self.__dict__["_pb"] = message

    def __getattr__(self, name):
        return getattr(self.__dict__["_pb"], name)

    def __setattr__(self, name, value):
        setattr(self.__dict__["_pb"], name, value)


@pb_bind(BoardDomain, "command_result", 1)
class BoardCommandResult(BoardMessage):
    BOARD_FIELD = "command_result"
    PAYLOAD_CLS = pb.CommandResult
    command = PbFieldInt("board.command_result.command")
    result = PbFieldInt("board.command_result.result")
    terminal = PbFieldBool("board.command_result.terminal")
    detail = PbFieldBytes("board.command_result.detail")


@pb_bind(BoardDomain, "board_info", 1)
class BoardInfoResponse(BoardMessage):
    BOARD_FIELD = "board_info"
    PAYLOAD_CLS = pb.GetBoardInfoResponse
    board_name = PbFieldBytes("board.board_info.board_name")
    hardware_revision = PbFieldBytes("board.board_info.hardware_revision")
    firmware_version = PbFieldBytes("board.board_info.firmware_version")
    protocol_variant = PbFieldBytes("board.board_info.protocol_variant")
    device_id = PbFieldBytes("board.board_info.device_id")
    active_runtime = PbFieldInt("board.board_info.active_runtime")
    implemented_sensor_count = PbFieldInt("board.board_info.implemented_sensor_count")


@pb_bind(BoardDomain, "sensor_descriptor", 1)
class ListSensorsResponse(BoardMessage):
    BOARD_FIELD = "sensor_descriptor"
    PAYLOAD_CLS = pb.ListSensorsResponse
    descriptor = PbFieldMsg("board.sensor_descriptor.descriptor", SensorDescriptor)
    next_cursor = PbFieldInt("board.sensor_descriptor.next_cursor")
    eof = PbFieldBool("board.sensor_descriptor.eof")

    def set_field_value(self, field, value):
        # PbFieldMsg fields cannot be assigned with setattr (protobuf rejects
        # direct assignment to message-typed fields); use CopyFrom instead.
        if isinstance(field, PbFieldMsg):
            path_nodes = field.path.split('.')
            root_node = self.message
            for node in path_nodes[:-1]:
                root_node = getattr(root_node, node)
            pb_value = value._pb if isinstance(value, SensorDescriptor) else value
            getattr(root_node, path_nodes[-1]).CopyFrom(pb_value)
        else:
            super().set_field_value(field, value)


@pb_bind(BoardDomain, "stream_configured", 1)
class ConfigureStreamResponse(BoardMessage):
    BOARD_FIELD = "stream_configured"
    PAYLOAD_CLS = pb.ConfigureStreamResponse
    sensor_id = PbFieldInt("board.stream_configured.sensor_id")
    actual_rate_millihz = PbFieldInt("board.stream_configured.actual_rate_millihz")
    flags = PbFieldInt("board.stream_configured.flags")


@pb_bind(BoardDomain, "calibration", 1)
class CalibrationResponse(BoardMessage):
    BOARD_FIELD = "calibration"
    PAYLOAD_CLS = pb.CalibrationResponse
    sensor_id = PbFieldInt("board.calibration.sensor_id")
    version = PbFieldInt("board.calibration.version")
    calibration_data = PbFieldBytes("board.calibration.calibration_data")
    persisted = PbFieldBool("board.calibration.persisted")
    crc32 = PbFieldInt("board.calibration.crc32")


@pb_bind(BoardDomain, "input_state", 1)
class InputStateResponse(BoardMessage):
    BOARD_FIELD = "input_state"
    PAYLOAD_CLS = pb.InputStateResponse
    sequence = PbFieldInt("board.input_state.sequence")
    timestamp_us = PbFieldInt("board.input_state.timestamp_us")
    buttons = PbFieldInt("board.input_state.buttons")
    gesture = PbFieldInt("board.input_state.gesture")
    microphone_threshold = PbFieldBool("board.input_state.microphone_threshold")
    mode = PbFieldInt("board.input_state.mode")


@pb_bind(BoardDomain, "i2c_result", 1)
class I2cTransferResponse(BoardMessage):
    BOARD_FIELD = "i2c_result"
    PAYLOAD_CLS = pb.I2cTransferResponse
    result = PbFieldInt("board.i2c_result.result")
    read_data = PbFieldBytes("board.i2c_result.read_data")
    bytes_written = PbFieldInt("board.i2c_result.bytes_written")
    bytes_read = PbFieldInt("board.i2c_result.bytes_read")


@pb_bind(BoardDomain, "gpio_configured", 1)
class GpioConfigureResponse(BoardMessage):
    BOARD_FIELD = "gpio_configured"
    PAYLOAD_CLS = pb.GpioConfigureResponse
    result = PbFieldInt("board.gpio_configured.result")
    pin = PbFieldInt("board.gpio_configured.pin")


@pb_bind(BoardDomain, "gpio_value", 1)
class GpioReadResponse(BoardMessage):
    BOARD_FIELD = "gpio_value"
    PAYLOAD_CLS = pb.GpioReadResponse
    result = PbFieldInt("board.gpio_value.result")
    pin = PbFieldInt("board.gpio_value.pin")
    value = PbFieldBool("board.gpio_value.value")


@pb_bind(BoardDomain, "adc_value", 1)
class AdcReadResponse(BoardMessage):
    BOARD_FIELD = "adc_value"
    PAYLOAD_CLS = pb.AdcReadResponse
    result = PbFieldInt("board.adc_value.result")
    channel = PbFieldInt("board.adc_value.channel")
    millivolts = PbFieldInt("board.adc_value.millivolts")
    raw = PbFieldInt("board.adc_value.raw")


@pb_bind(BoardDomain, "spi_result", 1)
class SpiTransferResponse(BoardMessage):
    BOARD_FIELD = "spi_result"
    PAYLOAD_CLS = pb.SpiTransferResponse
    result = PbFieldInt("board.spi_result.result")
    rx_data = PbFieldBytes("board.spi_result.rx_data")
    bytes_written = PbFieldInt("board.spi_result.bytes_written")
    bytes_read = PbFieldInt("board.spi_result.bytes_read")


@pb_bind(BoardDomain, "storage_status", 1)
class StorageInfoResponse(BoardMessage):
    BOARD_FIELD = "storage_status"
    PAYLOAD_CLS = pb.StorageInfoResponse
    state = PbFieldInt("board.storage_status.state")
    capacity_bytes = PbFieldInt("board.storage_status.capacity_bytes")
    used_bytes = PbFieldInt("board.storage_status.used_bytes")
    log_records = PbFieldInt("board.storage_status.log_records")
    erase_size = PbFieldInt("board.storage_status.erase_size")
    jedec_id = PbFieldBytes("board.storage_status.jedec_id")


@pb_bind(BoardDomain, "runtime_config", 1)
class RuntimeConfigResponse(BoardMessage):
    BOARD_FIELD = "runtime_config"
    PAYLOAD_CLS = pb.RuntimeConfigResponse
    active_runtime = PbFieldInt("board.runtime_config.active_runtime")
    persisted_runtime = PbFieldInt("board.runtime_config.persisted_runtime")
    persistence_available = PbFieldBool("board.runtime_config.persistence_available")
    ble_advertising = PbFieldBool("board.runtime_config.ble_advertising")
    ble_pairable = PbFieldBool("board.runtime_config.ble_pairable")
    ble_connected = PbFieldBool("board.runtime_config.ble_connected")
    bond_count = PbFieldInt("board.runtime_config.bond_count")
    event_log_filter = PbFieldInt("board.runtime_config.event_log_filter")
    raw_packet_log_filter = PbFieldInt("board.runtime_config.raw_packet_log_filter")


@pb_bind(BoardDomain, "remote_profile", 1)
class RemoteProfileResponse(BoardMessage):
    BOARD_FIELD = "remote_profile"
    PAYLOAD_CLS = pb.RemoteProfileResponse


@pb_bind(BoardDomain, "audio_configured", 1)
class AudioConfigureResponse(BoardMessage):
    BOARD_FIELD = "audio_configured"
    PAYLOAD_CLS = pb.AudioConfigureResponse
    actual_sample_rate_hz = PbFieldInt("board.audio_configured.actual_sample_rate_hz")
    actual_gain_db_x2 = PbFieldInt("board.audio_configured.actual_gain_db_x2")
    flags = PbFieldInt("board.audio_configured.flags")
