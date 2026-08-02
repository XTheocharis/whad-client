from queue import Empty, Full, Queue
from threading import Lock

from whad.device import Connector
from whad.exceptions import UnsupportedDomain
from whad.hub.board import BoardCommandResult, BoardStatus
from whad.hub.board.common import BoardDuplicateRequest, BoardPendingRequestFull, BoardRequestTimeout, PendingRequest
from whad.hub.discovery import Domain


class BoardConnector(Connector):
    domain = "board"
    MAX_PENDING_REQUESTS = 8
    MAX_RESPONSES_PER_REQUEST = 8
    MAX_EVENTS = 32
    TERMINAL_MESSAGE_NAMES = {
        "board_info",
        "sensor_descriptor",
        "sensor_sample",
        "stream_configured",
        "calibration",
        "input_state",
        "i2c_result",
        "gpio_configured",
        "gpio_value",
        "adc_value",
        "spi_result",
        "storage_status",
        "runtime_config",
        "remote_profile",
        "audio_configured",
    }

    def __init__(self, device=None, synchronous=False, max_pending=None, max_events=None):
        self.__ready = False
        self.__pending = {}
        self.__pending_lock = Lock()
        self.__next_request_id = 1
        self.__max_pending = max_pending or self.MAX_PENDING_REQUESTS
        self.__event_queue = Queue(maxsize=max_events or self.MAX_EVENTS)
        super().__init__(device)

        self.device.open()
        self.device.discover()

        if not self.device.has_domain(Domain.Board):
            raise UnsupportedDomain("Board")

        self.__ready = True
        self.enable_synchronous(synchronous)

    def close(self):
        self.device.close()

    def can_command(self, command):
        commands = self.device.get_domain_commands(Domain.Board) or 0
        return (commands & (1 << command)) > 0

    def get_board_info(self, timeout=None):
        return self.send_request(self.hub.board.create_get_board_info(), timeout=timeout)

    def list_sensors(self, cursor=0, timeout=None):
        return self.send_request(self.hub.board.create_list_sensors(cursor=cursor), timeout=timeout)

    def read_sensor(self, sensor_id, timeout=None):
        return self.send_request(self.hub.board.create_read_sensor(sensor_id=sensor_id), timeout=timeout)

    def configure_stream(self, sensor_id, rate_millihz, flags=0, timeout=None):
        message = self.hub.board.create_configure_stream(sensor_id=sensor_id, rate_millihz=rate_millihz, flags=flags)
        return self.send_request(message, timeout=timeout)

    def stop_stream(self, sensor_id, timeout=None):
        return self.send_request(self.hub.board.create_stop_stream(sensor_id=sensor_id), timeout=timeout)

    def calibrate(self, sensor_id, flags=0, persist=False, timeout=None):
        message = self.hub.board.create_calibrate(sensor_id=sensor_id, flags=flags, persist=persist)
        request_id = self.begin_request(message)
        self.send_message(message)
        while True:
            resp = self.wait_response(request_id, timeout=timeout)
            if self.is_terminal_response(resp):
                return resp

    def calibrate_imu(self, flags=0, persist=False, timeout=None):
        return self.calibrate(sensor_id=1, flags=flags, persist=persist, timeout=timeout)

    def calibrate_mag(self, flags=0, persist=False, timeout=None):
        return self.calibrate(sensor_id=3, flags=flags, persist=persist, timeout=timeout)

    SENSOR_ID_COLOR = 10
    SENSOR_ID_PROXIMITY = 11
    SENSOR_ID_GESTURE = 12

    def read_color(self, timeout=None):
        return self.read_sensor(self.SENSOR_ID_COLOR, timeout=timeout)

    def read_proximity(self, timeout=None):
        return self.read_sensor(self.SENSOR_ID_PROXIMITY, timeout=timeout)

    def read_gesture(self, timeout=None):
        return self.read_sensor(self.SENSOR_ID_GESTURE, timeout=timeout)

    def stream_color(self, rate_millihz, flags=0, timeout=None):
        return self.configure_stream(
            self.SENSOR_ID_COLOR, rate_millihz, flags=flags, timeout=timeout)

    def stream_proximity(self, rate_millihz, flags=0, timeout=None):
        return self.configure_stream(
            self.SENSOR_ID_PROXIMITY, rate_millihz, flags=flags, timeout=timeout)

    def get_calibration(self, sensor_id, timeout=None):
        message = self.hub.board.create_get_calibration(sensor_id=sensor_id)
        return self.send_request(message, timeout=timeout)

    def motion_samples(self, sensor_id=None, timeout=0.5):
        """Generator yielding SensorSample events from active streams.

        If sensor_id is given, yields only samples for that sensor.
        Otherwise yields all SensorSample events.
        """
        from whad.hub.board import SensorSample
        while True:
            event = self.next_event(timeout=timeout)
            if event is None:
                continue
            if not isinstance(event, SensorSample):
                continue
            if sensor_id is not None and event.sensor_id != sensor_id:
                continue
            yield event

    def next_event(self, timeout=None):
        try:
            return self.__event_queue.get(block=True, timeout=timeout)
        except Empty:
            return None

    def get_input_state(self, timeout=None):
        return self.send_request(
            self.hub.board.create_get_input_state(), timeout=timeout)

    def configure_input(self, mode, flags=0, dwell_ms=0, deadzone=0,
                        persist=False, timeout=None):
        message = self.hub.board.create_configure_input(
            mode=mode, flags=flags, dwell_ms=dwell_ms,
            deadzone=deadzone, persist=persist)
        return self.send_request(message, timeout=timeout)

    def remote_profile_get(self, profile_id, timeout=None):
        return self.send_request(
            self.hub.board.create_remote_profile_get(profile_id=profile_id),
            timeout=timeout)

    def remote_profile_set(self, profile_id, name, sensitivity=0, deadzone=0,
                           pointer_mode=False, tilt_mode=False,
                           persist=False, timeout=None):
        message = self.hub.board.create_remote_profile_set(persist=persist)
        profile = message.message.board.remote_profile_set.profile
        profile.profile_id = profile_id
        profile.name = name
        profile.sensitivity = sensitivity
        profile.deadzone = deadzone
        profile.pointer_mode = pointer_mode
        profile.tilt_mode = tilt_mode
        return self.send_request(message, timeout=timeout)

    def configure_audio(self, enabled=True, sample_rate_hz=16000,
                        gain_db_x2=40, flags=0, timeout=None):
        message = self.hub.board.create_audio_configure(
            enabled=enabled, sample_rate_hz=sample_rate_hz,
            gain_db_x2=gain_db_x2, flags=flags)
        return self.send_request(message, timeout=timeout)

    def audio_metrics(self, timeout=0.5):
        """Generator yielding SensorSample events for the audio_level
        sensor (ID 13). Requires a ConfigureStream subscription first."""
        from whad.hub.board import SensorSample
        while True:
            event = self.next_event(timeout=timeout)
            if event is None:
                continue
            if not isinstance(event, SensorSample):
                continue
            if event.sensor_id != 13:
                continue
            yield event

    def raw_pcm_diagnostics(self, duration_ms, chunk_size=40, timeout=None):
        message = self.hub.board.create_raw_pcm_diagnostics(
            duration_ms=duration_ms, chunk_size=chunk_size)
        request_id = self.begin_request(message)
        self.send_message(message)
        while True:
            resp = self.wait_response(request_id, timeout=timeout)
            yield resp
            if self.is_terminal_response(resp):
                self.retire_request(request_id)
                break

    OUTPUT_TARGET_BUZZER = 1
    OUTPUT_TARGET_NEOPIXEL = 2
    OUTPUT_TARGET_WHITE_LED = 3
    OUTPUT_TARGET_RED_LED = 4
    OUTPUT_TARGET_BACKLIGHT = 5

    def set_output(self, target, value=0, duration_ms=0, force=False,
                   timeout=None):
        message = self.hub.board.create_set_output(
            target=target, value=value, duration_ms=duration_ms,
            force=force)
        return self.send_request(message, timeout=timeout)

    def stop_output(self, target, force=False, timeout=None):
        message = self.hub.board.create_set_output(
            target=target, stop=True, force=force)
        return self.send_request(message, timeout=timeout)

    def set_buzzer(self, freq_hz, duration_ms=200, timeout=None):
        return self.set_output(
            self.OUTPUT_TARGET_BUZZER, value=freq_hz,
            duration_ms=duration_ms, timeout=timeout)

    def stop_buzzer(self, timeout=None):
        return self.stop_output(self.OUTPUT_TARGET_BUZZER, timeout=timeout)

    def set_neopixel(self, r, g, b, timeout=None):
        packed = ((int(r) & 0xFF) << 16) | ((int(g) & 0xFF) << 8) | (int(b) & 0xFF)
        return self.set_output(
            self.OUTPUT_TARGET_NEOPIXEL, value=packed, timeout=timeout)

    def set_white_led(self, on, timeout=None):
        return self.set_output(
            self.OUTPUT_TARGET_WHITE_LED, value=1 if on else 0,
            timeout=timeout)

    def set_red_led(self, on, timeout=None):
        return self.set_output(
            self.OUTPUT_TARGET_RED_LED, value=1 if on else 0,
            timeout=timeout)

    def set_backlight(self, on, timeout=None):
        return self.set_output(
            self.OUTPUT_TARGET_BACKLIGHT, value=1 if on else 0,
            timeout=timeout)

    RESOURCE_GPIO_PIN = 1
    RESOURCE_I2C_BUS = 2
    RESOURCE_SPI_BUS = 3
    RESOURCE_ADC_CHANNEL = 4
    RESOURCE_OUTPUT = 5
    RESOURCE_STORAGE = 6

    def i2c_transfer(self, address, write_data=b"", read_length=0,
                     repeated_start=False, frequency_hz=400000,
                     force=False, timeout=None):
        message = self.hub.board.create_i2c_transfer(
            address=address, write_data=write_data,
            read_length=read_length, repeated_start=repeated_start,
            frequency_hz=frequency_hz, force=force)
        return self.send_request(message, timeout=timeout)

    def i2c_write(self, address, data, frequency_hz=400000,
                  force=False, timeout=None):
        return self.i2c_transfer(
            address, write_data=data, read_length=0,
            frequency_hz=frequency_hz, force=force, timeout=timeout)

    def i2c_read(self, address, read_length, frequency_hz=400000,
                 force=False, timeout=None):
        return self.i2c_transfer(
            address, write_data=b"", read_length=read_length,
            frequency_hz=frequency_hz, force=force, timeout=timeout)

    def spi_transfer(self, cs_pin, frequency_hz=1000000, mode=1,
                     tx_data=b"", read_length=0, force=False,
                     timeout=None):
        message = self.hub.board.create_spi_transfer(
            cs_pin=cs_pin, frequency_hz=frequency_hz, mode=mode,
            tx_data=tx_data, read_length=read_length, force=force)
        return self.send_request(message, timeout=timeout)

    def release_pin(self, resource, instance, timeout=None):
        message = self.hub.board.create_release_pin(
            resource=resource, instance=instance)
        return self.send_request(message, timeout=timeout)

    def get_hid_status(self, timeout=None):
        return self.send_request(
            self.hub.board.create_get_runtime_config(), timeout=timeout)

    def storage_info(self, timeout=None):
        return self.send_request(
            self.hub.board.create_storage_info(), timeout=timeout)

    def storage_adopt(self, confirm_nonce, force=False, timeout=None):
        message = self.hub.board.create_storage_adopt(
            confirm_nonce=confirm_nonce, force=force)
        return self.send_request(message, timeout=timeout, keep_pending=True)

    def storage_read_log(self, cursor=0, max_bytes=256, timeout=None):
        message = self.hub.board.create_storage_read_log(
            cursor=cursor, max_bytes=max_bytes)
        return self.send_request(message, timeout=timeout, keep_pending=True)

    def storage_read_log_all(self, max_bytes=256, timeout=None):
        """Read the entire log via cursor-based chunk reconstruction.

        Yields LogChunk messages until EOF or error. Each chunk carries
        cursor/offset/count/total fields for reassembly.
        """
        from whad.hub.board import LogChunk
        cursor = 0
        while True:
            chunk = self.storage_read_log(
                cursor=cursor, max_bytes=max_bytes, timeout=timeout)
            if chunk is None:
                break
            yield chunk
            if getattr(chunk, "eof", False):
                break
            if getattr(chunk, "result", 0) != 0:
                break
            cursor = getattr(chunk, "cursor", cursor) + getattr(chunk, "count", 0)

    def storage_erase_log(self, confirm_nonce, timeout=None):
        message = self.hub.board.create_storage_erase_log(
            confirm_nonce=confirm_nonce)
        return self.send_request(message, timeout=timeout, keep_pending=True)

    def start_pairing(self, duration_ms=30000, timeout=None):
        message = self.hub.board.create("set_runtime_config")
        message.message.board.set_runtime_config.open_pairing_window.duration_ms = duration_ms
        return self.send_request(message, timeout=timeout)

    def forget_bonds(self, confirm_nonce, timeout=None):
        message = self.hub.board.create("set_runtime_config")
        message.message.board.set_runtime_config.clear_bonds.confirm_nonce = confirm_nonce
        return self.send_request(message, timeout=timeout)

    def send_request(self, message, timeout=None, keep_pending=False):
        request_id = self.begin_request(message)
        pending = self.__pending[request_id]
        self.send_message(message)
        response = pending.get(timeout=timeout)
        if self.is_terminal_response(response) and not keep_pending:
            self.retire_request(request_id)
        return response

    def begin_request(self, message):
        request_id = message.request_id or self.allocate_request_id()
        message.request_id = request_id
        with self.__pending_lock:
            if request_id in self.__pending:
                raise BoardDuplicateRequest("duplicate Board request_id")
            if len(self.__pending) >= self.__max_pending:
                raise BoardPendingRequestFull("Board pending request table is full")
            self.__pending[request_id] = PendingRequest(request_id, self.MAX_RESPONSES_PER_REQUEST)
        return request_id

    def wait_response(self, request_id, timeout=None):
        with self.__pending_lock:
            pending = self.__pending.get(request_id)
        if pending is None:
            raise BoardRequestTimeout("Board request is not pending")
        response = pending.get(timeout=timeout)
        if self.is_terminal_response(response):
            self.retire_request(request_id)
        return response

    def retire_request(self, request_id):
        with self.__pending_lock:
            self.__pending.pop(request_id, None)

    def allocate_request_id(self):
        with self.__pending_lock:
            for _ in range(0xFFFFFFFF):
                request_id = self.__next_request_id
                self.__next_request_id += 1
                if self.__next_request_id > 0xFFFFFFFF:
                    self.__next_request_id = 1
                if request_id not in self.__pending:
                    return request_id
        raise BoardPendingRequestFull("no Board request_id is available")

    def on_domain_msg(self, domain, message):
        if domain != self.domain or not self.__ready:
            return
        request_id = getattr(message, "request_id", 0)
        if request_id == 0:
            self.enqueue_event(message)
            return
        self.dispatch_response(request_id, message)

    def enqueue_event(self, message):
        try:
            self.__event_queue.put_nowait(message)
            return True
        except Full:
            return False

    def dispatch_response(self, request_id, message):
        with self.__pending_lock:
            pending = self.__pending.get(request_id)
        if pending is None:
            self.on_late_response(message)
            return False
        if pending.terminal_seen and self.is_terminal_response(message):
            self.on_late_response(message)
            return False
        if self.is_terminal_response(message):
            pending.terminal_seen = True
        return pending.put(message)

    def on_late_response(self, message):
        return None

    def is_terminal_response(self, message):
        if isinstance(message, BoardCommandResult):
            return message.terminal
        if isinstance(message, BoardStatus):
            return message.terminal
        if message.message_name in ("audio_chunk", "log_chunk"):
            return bool(message.eof) or message.result != 0
        return message.message_name in self.TERMINAL_MESSAGE_NAMES

    def on_discovery_msg(self, message):
        pass

    def on_generic_msg(self, message):
        pass

    def on_packet(self, packet):
        pass

    def on_event(self, event):
        pass


Board = BoardConnector

__all__ = ["BoardConnector", "Board"]
