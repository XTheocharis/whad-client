from whad.hub import ProtocolHub
from whad.hub.message import HubMessage, pb_bind
from whad.hub.registry import Registry


class Commands:
    GetBoardInfo = 0x00
    ListSensors = 0x01
    ReadSensor = 0x02
    ConfigureStream = 0x03
    StopStream = 0x04
    Calibrate = 0x05
    GetCalibration = 0x06
    SetOutput = 0x07
    GetInputState = 0x08
    ConfigureInput = 0x09
    I2cTransfer = 0x0A
    GpioConfigure = 0x0B
    GpioRead = 0x0C
    GpioWrite = 0x0D
    AdcRead = 0x0E
    SpiTransfer = 0x0F
    StorageInfo = 0x10
    StorageAdopt = 0x11
    StorageReadLog = 0x12
    StorageEraseLog = 0x13
    GetRuntimeConfig = 0x14
    SetRuntimeConfig = 0x15
    SetRuntimeMode = 0x16
    RemoteProfileGet = 0x17
    RemoteProfileSet = 0x18
    AudioConfigure = 0x19
    ReleasePin = 0x1A
    RawPcmDiagnostics = 0x1B


@pb_bind(ProtocolHub, name="board", version=1)
class BoardDomain(Registry):
    NAME = "board"
    VERSIONS = {}

    def __init__(self, version: int):
        self.proto_version = version

    @staticmethod
    def parse(proto_version: int, message) -> HubMessage:
        message_type = message.board.WhichOneof("msg")
        message_clazz = BoardDomain.bound(message_type, proto_version)
        return message_clazz.parse(proto_version, message)

    def create(self, name, request_id=0, **kwargs):
        return BoardDomain.bound(name, self.proto_version)(request_id=request_id, **kwargs)

    def create_get_board_info(self, request_id=0):
        return self.create("get_board_info", request_id=request_id)

    def create_list_sensors(self, request_id=0, cursor=0):
        return self.create("list_sensors", request_id=request_id, cursor=cursor)

    def create_read_sensor(self, request_id=0, sensor_id=0):
        return self.create("read_sensor", request_id=request_id, sensor_id=sensor_id)

    def create_configure_stream(self, request_id=0, sensor_id=0, rate_millihz=0, flags=0):
        return self.create("configure_stream", request_id=request_id, sensor_id=sensor_id, rate_millihz=rate_millihz, flags=flags)

    def create_stop_stream(self, request_id=0, sensor_id=0):
        return self.create("stop_stream", request_id=request_id, sensor_id=sensor_id)

    def create_calibrate(self, request_id=0, sensor_id=0, flags=0, persist=False):
        return self.create("calibrate", request_id=request_id, sensor_id=sensor_id, flags=flags, persist=persist)

    def create_get_calibration(self, request_id=0, sensor_id=0):
        return self.create("get_calibration", request_id=request_id, sensor_id=sensor_id)

    def create_set_output(self, request_id=0, target=0, value=0, duration_ms=0, stop=False, force=False):
        return self.create("set_output", request_id=request_id, target=target, value=value, duration_ms=duration_ms, stop=stop, force=force)

    def create_get_input_state(self, request_id=0):
        return self.create("get_input_state", request_id=request_id)

    def create_configure_input(self, request_id=0, mode=0, flags=0, dwell_ms=0, deadzone=0, persist=False):
        return self.create("configure_input", request_id=request_id, mode=mode, flags=flags, dwell_ms=dwell_ms, deadzone=deadzone, persist=persist)

    def create_i2c_transfer(self, request_id=0, address=0, write_data=b"", read_length=0, repeated_start=False, frequency_hz=400000, force=False):
        return self.create("i2c_transfer", request_id=request_id, address=address, write_data=write_data, read_length=read_length, repeated_start=repeated_start, frequency_hz=frequency_hz, force=force)

    def create_gpio_configure(self, request_id=0, pin=0, direction=0, pull=0, initial_value=False, force=False):
        return self.create("gpio_configure", request_id=request_id, pin=pin, direction=direction, pull=pull, initial_value=initial_value, force=force)

    def create_gpio_read(self, request_id=0, pin=0, force=False):
        return self.create("gpio_read", request_id=request_id, pin=pin, force=force)

    def create_gpio_write(self, request_id=0, pin=0, value=False):
        return self.create("gpio_write", request_id=request_id, pin=pin, value=value)

    def create_adc_read(self, request_id=0, channel=0, samples=1):
        return self.create("adc_read", request_id=request_id, channel=channel, samples=samples)

    def create_spi_transfer(self, request_id=0, cs_pin=0, frequency_hz=1000000, mode=1, tx_data=b"", read_length=0, force=False):
        return self.create("spi_transfer", request_id=request_id, cs_pin=cs_pin, frequency_hz=frequency_hz, mode=mode, tx_data=tx_data, read_length=read_length, force=force)

    def create_storage_info(self, request_id=0):
        return self.create("storage_info", request_id=request_id)

    def create_storage_adopt(self, request_id=0, confirm_nonce=0, force=False):
        return self.create("storage_adopt", request_id=request_id, confirm_nonce=confirm_nonce, force=force)

    def create_storage_read_log(self, request_id=0, cursor=0, max_bytes=256):
        return self.create("storage_read_log", request_id=request_id, cursor=cursor, max_bytes=max_bytes)

    def create_storage_erase_log(self, request_id=0, confirm_nonce=0):
        return self.create("storage_erase_log", request_id=request_id, confirm_nonce=confirm_nonce)

    def create_get_runtime_config(self, request_id=0):
        return self.create("get_runtime_config", request_id=request_id)

    def create_set_runtime_mode(self, request_id=0, runtime=0, persist=False, reboot=False):
        return self.create("set_runtime_mode", request_id=request_id, runtime=runtime, persist=persist, reboot=reboot)

    def create_remote_profile_get(self, request_id=0, profile_id=0):
        return self.create("remote_profile_get", request_id=request_id, profile_id=profile_id)

    def create_remote_profile_set(self, request_id=0, persist=False):
        return self.create("remote_profile_set", request_id=request_id, persist=persist)

    def create_audio_configure(self, request_id=0, enabled=False, sample_rate_hz=16000, gain_db_x2=40, flags=0):
        return self.create("audio_configure", request_id=request_id, enabled=enabled, sample_rate_hz=sample_rate_hz, gain_db_x2=gain_db_x2, flags=flags)

    def create_release_pin(self, request_id=0, resource=0, instance=0):
        return self.create("release_pin", request_id=request_id, resource=resource, instance=instance)

    def create_raw_pcm_diagnostics(self, request_id=0, duration_ms=0, chunk_size=128):
        return self.create("raw_pcm_diagnostics", request_id=request_id, duration_ms=duration_ms, chunk_size=chunk_size)

    def create_command_result(self, request_id=0, command=0, result=0, terminal=True, detail=""):
        return self.create("command_result", request_id=request_id, command=command, result=result, terminal=terminal, detail=detail)

    def create_board_info_response(self, request_id=0, board_name="", hardware_revision="", firmware_version="", protocol_variant="", device_id=b"", active_runtime=0, implemented_sensor_count=0):
        return self.create("board_info", request_id=request_id, board_name=board_name, hardware_revision=hardware_revision, firmware_version=firmware_version, protocol_variant=protocol_variant, device_id=device_id, active_runtime=active_runtime, implemented_sensor_count=implemented_sensor_count)

    def create_sensor_sample(self, request_id=0, sensor_id=0, sequence=0, timestamp_us=0, status=0, values=None):
        msg = self.create("sensor_sample", request_id=request_id, sensor_id=sensor_id, sequence=sequence, timestamp_us=timestamp_us, status=status)
        if values is not None:
            msg.values.extend(values)
        return msg
