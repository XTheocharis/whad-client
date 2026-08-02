from whad.hub.message import PbFieldBool, PbFieldBytes, PbFieldInt
from whad.protocol.board import board_pb2 as pb

from .common import BoardMessage
from .domain import BoardDomain
from ..message import pb_bind


@pb_bind(BoardDomain, "get_board_info", 1)
class GetBoardInfoRequest(BoardMessage):
    BOARD_FIELD = "get_board_info"
    PAYLOAD_CLS = pb.GetBoardInfoRequest


@pb_bind(BoardDomain, "list_sensors", 1)
class ListSensorsRequest(BoardMessage):
    BOARD_FIELD = "list_sensors"
    PAYLOAD_CLS = pb.ListSensorsRequest
    cursor = PbFieldInt("board.list_sensors.cursor")


@pb_bind(BoardDomain, "read_sensor", 1)
class ReadSensorRequest(BoardMessage):
    BOARD_FIELD = "read_sensor"
    PAYLOAD_CLS = pb.ReadSensorRequest
    sensor_id = PbFieldInt("board.read_sensor.sensor_id")


@pb_bind(BoardDomain, "configure_stream", 1)
class ConfigureStreamRequest(BoardMessage):
    BOARD_FIELD = "configure_stream"
    PAYLOAD_CLS = pb.ConfigureStreamRequest
    sensor_id = PbFieldInt("board.configure_stream.sensor_id")
    rate_millihz = PbFieldInt("board.configure_stream.rate_millihz")
    flags = PbFieldInt("board.configure_stream.flags")


@pb_bind(BoardDomain, "stop_stream", 1)
class StopStreamRequest(BoardMessage):
    BOARD_FIELD = "stop_stream"
    PAYLOAD_CLS = pb.StopStreamRequest
    sensor_id = PbFieldInt("board.stop_stream.sensor_id")


@pb_bind(BoardDomain, "calibrate", 1)
class CalibrateRequest(BoardMessage):
    BOARD_FIELD = "calibrate"
    PAYLOAD_CLS = pb.CalibrateRequest
    sensor_id = PbFieldInt("board.calibrate.sensor_id")
    flags = PbFieldInt("board.calibrate.flags")
    persist = PbFieldBool("board.calibrate.persist")


@pb_bind(BoardDomain, "get_calibration", 1)
class GetCalibrationRequest(BoardMessage):
    BOARD_FIELD = "get_calibration"
    PAYLOAD_CLS = pb.GetCalibrationRequest
    sensor_id = PbFieldInt("board.get_calibration.sensor_id")


@pb_bind(BoardDomain, "set_output", 1)
class SetOutputRequest(BoardMessage):
    BOARD_FIELD = "set_output"
    PAYLOAD_CLS = pb.SetOutputRequest
    target = PbFieldInt("board.set_output.target")
    value = PbFieldInt("board.set_output.value")
    duration_ms = PbFieldInt("board.set_output.duration_ms")
    stop = PbFieldBool("board.set_output.stop")
    force = PbFieldBool("board.set_output.force")


@pb_bind(BoardDomain, "get_input_state", 1)
class GetInputStateRequest(BoardMessage):
    BOARD_FIELD = "get_input_state"
    PAYLOAD_CLS = pb.GetInputStateRequest


@pb_bind(BoardDomain, "configure_input", 1)
class ConfigureInputRequest(BoardMessage):
    BOARD_FIELD = "configure_input"
    PAYLOAD_CLS = pb.ConfigureInputRequest
    mode = PbFieldInt("board.configure_input.mode")
    flags = PbFieldInt("board.configure_input.flags")
    dwell_ms = PbFieldInt("board.configure_input.dwell_ms")
    deadzone = PbFieldInt("board.configure_input.deadzone")
    persist = PbFieldBool("board.configure_input.persist")


@pb_bind(BoardDomain, "i2c_transfer", 1)
class I2cTransferRequest(BoardMessage):
    BOARD_FIELD = "i2c_transfer"
    PAYLOAD_CLS = pb.I2cTransferRequest
    address = PbFieldInt("board.i2c_transfer.address")
    write_data = PbFieldBytes("board.i2c_transfer.write_data")
    read_length = PbFieldInt("board.i2c_transfer.read_length")
    repeated_start = PbFieldBool("board.i2c_transfer.repeated_start")
    frequency_hz = PbFieldInt("board.i2c_transfer.frequency_hz")
    force = PbFieldBool("board.i2c_transfer.force")


@pb_bind(BoardDomain, "gpio_configure", 1)
class GpioConfigureRequest(BoardMessage):
    BOARD_FIELD = "gpio_configure"
    PAYLOAD_CLS = pb.GpioConfigureRequest
    pin = PbFieldInt("board.gpio_configure.pin")
    direction = PbFieldInt("board.gpio_configure.direction")
    pull = PbFieldInt("board.gpio_configure.pull")
    initial_value = PbFieldBool("board.gpio_configure.initial_value")
    force = PbFieldBool("board.gpio_configure.force")


@pb_bind(BoardDomain, "gpio_read", 1)
class GpioReadRequest(BoardMessage):
    BOARD_FIELD = "gpio_read"
    PAYLOAD_CLS = pb.GpioReadRequest
    pin = PbFieldInt("board.gpio_read.pin")
    force = PbFieldBool("board.gpio_read.force")


@pb_bind(BoardDomain, "gpio_write", 1)
class GpioWriteRequest(BoardMessage):
    BOARD_FIELD = "gpio_write"
    PAYLOAD_CLS = pb.GpioWriteRequest
    pin = PbFieldInt("board.gpio_write.pin")
    value = PbFieldBool("board.gpio_write.value")


@pb_bind(BoardDomain, "adc_read", 1)
class AdcReadRequest(BoardMessage):
    BOARD_FIELD = "adc_read"
    PAYLOAD_CLS = pb.AdcReadRequest
    channel = PbFieldInt("board.adc_read.channel")
    samples = PbFieldInt("board.adc_read.samples")


@pb_bind(BoardDomain, "spi_transfer", 1)
class SpiTransferRequest(BoardMessage):
    BOARD_FIELD = "spi_transfer"
    PAYLOAD_CLS = pb.SpiTransferRequest
    cs_pin = PbFieldInt("board.spi_transfer.cs_pin")
    frequency_hz = PbFieldInt("board.spi_transfer.frequency_hz")
    mode = PbFieldInt("board.spi_transfer.mode")
    tx_data = PbFieldBytes("board.spi_transfer.tx_data")
    read_length = PbFieldInt("board.spi_transfer.read_length")
    force = PbFieldBool("board.spi_transfer.force")


@pb_bind(BoardDomain, "storage_info", 1)
class StorageInfoRequest(BoardMessage):
    BOARD_FIELD = "storage_info"
    PAYLOAD_CLS = pb.StorageInfoRequest


@pb_bind(BoardDomain, "storage_adopt", 1)
class StorageAdoptRequest(BoardMessage):
    BOARD_FIELD = "storage_adopt"
    PAYLOAD_CLS = pb.StorageAdoptRequest
    confirm_nonce = PbFieldInt("board.storage_adopt.confirm_nonce")
    force = PbFieldBool("board.storage_adopt.force")


@pb_bind(BoardDomain, "storage_read_log", 1)
class StorageReadLogRequest(BoardMessage):
    BOARD_FIELD = "storage_read_log"
    PAYLOAD_CLS = pb.StorageReadLogRequest
    cursor = PbFieldInt("board.storage_read_log.cursor")
    max_bytes = PbFieldInt("board.storage_read_log.max_bytes")


@pb_bind(BoardDomain, "storage_erase_log", 1)
class StorageEraseLogRequest(BoardMessage):
    BOARD_FIELD = "storage_erase_log"
    PAYLOAD_CLS = pb.StorageEraseLogRequest
    confirm_nonce = PbFieldInt("board.storage_erase_log.confirm_nonce")


@pb_bind(BoardDomain, "get_runtime_config", 1)
class GetRuntimeConfigRequest(BoardMessage):
    BOARD_FIELD = "get_runtime_config"
    PAYLOAD_CLS = pb.GetRuntimeConfigRequest


@pb_bind(BoardDomain, "set_runtime_config", 1)
class SetRuntimeConfigRequest(BoardMessage):
    BOARD_FIELD = "set_runtime_config"
    PAYLOAD_CLS = pb.SetRuntimeConfigRequest


@pb_bind(BoardDomain, "set_runtime_mode", 1)
class SetRuntimeModeRequest(BoardMessage):
    BOARD_FIELD = "set_runtime_mode"
    PAYLOAD_CLS = pb.SetRuntimeModeRequest
    runtime = PbFieldInt("board.set_runtime_mode.runtime")
    persist = PbFieldBool("board.set_runtime_mode.persist")
    reboot = PbFieldBool("board.set_runtime_mode.reboot")


@pb_bind(BoardDomain, "remote_profile_get", 1)
class RemoteProfileGetRequest(BoardMessage):
    BOARD_FIELD = "remote_profile_get"
    PAYLOAD_CLS = pb.RemoteProfileGetRequest
    profile_id = PbFieldInt("board.remote_profile_get.profile_id")


@pb_bind(BoardDomain, "remote_profile_set", 1)
class RemoteProfileSetRequest(BoardMessage):
    BOARD_FIELD = "remote_profile_set"
    PAYLOAD_CLS = pb.RemoteProfileSetRequest
    persist = PbFieldBool("board.remote_profile_set.persist")


@pb_bind(BoardDomain, "audio_configure", 1)
class AudioConfigureRequest(BoardMessage):
    BOARD_FIELD = "audio_configure"
    PAYLOAD_CLS = pb.AudioConfigureRequest
    enabled = PbFieldBool("board.audio_configure.enabled")
    sample_rate_hz = PbFieldInt("board.audio_configure.sample_rate_hz")
    gain_db_x2 = PbFieldInt("board.audio_configure.gain_db_x2")
    flags = PbFieldInt("board.audio_configure.flags")


@pb_bind(BoardDomain, "release_pin", 1)
class ReleasePinRequest(BoardMessage):
    BOARD_FIELD = "release_pin"
    PAYLOAD_CLS = pb.ReleasePinRequest
    resource = PbFieldInt("board.release_pin.resource")
    instance = PbFieldInt("board.release_pin.instance")


@pb_bind(BoardDomain, "raw_pcm_diagnostics", 1)
class RawPcmDiagnosticsRequest(BoardMessage):
    BOARD_FIELD = "raw_pcm_diagnostics"
    PAYLOAD_CLS = pb.RawPcmDiagnosticsRequest
    duration_ms = PbFieldInt("board.raw_pcm_diagnostics.duration_ms")
    chunk_size = PbFieldInt("board.raw_pcm_diagnostics.chunk_size")
