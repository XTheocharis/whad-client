import argparse
import sys


def parse_int(value):
    return int(value, 0)


def parse_hex(value):
    return bytes.fromhex(value.replace(":", ""))


def print_response(response):
    print(response)


def require_flag(args, attr, message):
    if not getattr(args, attr):
        raise SystemExit(message)


def request_info(connector, args):
    return connector.get_board_info(timeout=args.timeout)


def request_runtime_config(connector, args):
    return connector.send_request(connector.hub.board.create_get_runtime_config(), timeout=args.timeout)


def request_runtime_mode(connector, args):
    message = connector.hub.board.create_set_runtime_mode(runtime=args.mode, persist=args.persist, reboot=args.reboot)
    return connector.send_request(message, timeout=args.timeout)


def request_runtime_open_pairing(connector, args):
    message = connector.hub.board.create("set_runtime_config")
    message.message.board.set_runtime_config.open_pairing_window.duration_ms = args.duration_ms
    return connector.send_request(message, timeout=args.timeout)


def request_runtime_clear_bonds(connector, args):
    require_flag(args, "yes_really_clear_bonds", "clear-bonds requires --yes-really-clear-bonds")
    message = connector.hub.board.create("set_runtime_config")
    message.message.board.set_runtime_config.clear_bonds.confirm_nonce = args.confirm_nonce
    return connector.send_request(message, timeout=args.timeout)


def request_sensor_list(connector, args):
    return connector.send_request(connector.hub.board.create_list_sensors(cursor=args.cursor), timeout=args.timeout)


def request_sensor_read(connector, args):
    return connector.read_sensor(args.sensor_id, timeout=args.timeout)


def request_stream_start(connector, args):
    return connector.configure_stream(args.sensor_id, args.rate_millihz, flags=args.flags, timeout=args.timeout)


def request_stream_stop(connector, args):
    return connector.stop_stream(args.sensor_id, timeout=args.timeout)


def request_calibration_run(connector, args):
    message = connector.hub.board.create_calibrate(sensor_id=args.sensor_id, flags=args.flags, persist=args.persist)
    return connector.send_request(message, timeout=args.timeout, keep_pending=True)


def request_calibrate_imu(connector, args):
    return connector.calibrate_imu(flags=args.flags, persist=args.persist, timeout=args.timeout)


def request_calibrate_mag(connector, args):
    return connector.calibrate_mag(flags=args.flags, persist=args.persist, timeout=args.timeout)


def request_calibration_get(connector, args):
    message = connector.hub.board.create_get_calibration(sensor_id=args.sensor_id)
    return connector.send_request(message, timeout=args.timeout)


def request_input_state(connector, args):
    return connector.send_request(connector.hub.board.create_get_input_state(), timeout=args.timeout)


def request_input_configure(connector, args):
    message = connector.hub.board.create_configure_input(mode=args.mode, flags=args.flags, dwell_ms=args.dwell_ms, deadzone=args.deadzone, persist=args.persist)
    return connector.send_request(message, timeout=args.timeout)


def request_audio_configure(connector, args):
    message = connector.hub.board.create_audio_configure(enabled=args.enabled, sample_rate_hz=args.sample_rate_hz, gain_db_x2=args.gain_db_x2, flags=args.flags)
    return connector.send_request(message, timeout=args.timeout)


def request_raw_pcm(connector, args):
    message = connector.hub.board.create_raw_pcm_diagnostics(duration_ms=args.duration_ms, chunk_size=args.chunk_size)
    return connector.send_request(message, timeout=args.timeout, keep_pending=True)


def request_audio_metrics(connector, args):
    stream_msg = connector.hub.board.create_configure_stream(
        sensor_id=13, rate_millihz=20000, flags=0)
    connector.send_request(stream_msg, timeout=args.timeout)
    count = 0
    try:
        for sample in connector.audio_metrics(timeout=args.timeout):
            dbfs = sample.values[0] if sample.values else 0
            print(f"audio_level seq={sample.sequence} dbfs_x1000={dbfs}")
            count += 1
            if args.count > 0 and count >= args.count:
                break
    except KeyboardInterrupt:
        pass
    connector.stop_stream(sensor_id=13, timeout=args.timeout)
    return None


def request_output_set(connector, args):
    message = connector.hub.board.create_set_output(target=args.target, value=args.value, duration_ms=args.duration_ms, force=args.force)
    return connector.send_request(message, timeout=args.timeout)


def request_output_stop(connector, args):
    message = connector.hub.board.create_set_output(target=args.target, stop=True, force=args.force)
    return connector.send_request(message, timeout=args.timeout)


def request_output_buzzer(connector, args):
    return connector.set_buzzer(args.frequency, duration_ms=args.duration_ms, timeout=args.timeout)


def request_output_neopixel(connector, args):
    return connector.set_neopixel(args.red, args.green, args.blue, timeout=args.timeout)


def request_output_white(connector, args):
    return connector.set_white_led(bool(args.value), timeout=args.timeout)


def request_output_red(connector, args):
    return connector.set_red_led(bool(args.value), timeout=args.timeout)


def request_output_backlight(connector, args):
    return connector.set_backlight(bool(args.value), timeout=args.timeout)


def request_storage_info(connector, args):
    return connector.storage_info(timeout=args.timeout)


def request_storage_adopt(connector, args):
    require_flag(args, "yes_really_adopt_and_erase", "storage adopt requires --yes-really-adopt-and-erase")
    return connector.storage_adopt(confirm_nonce=args.confirm_nonce, force=args.force, timeout=args.timeout)


def request_storage_read_log(connector, args):
    return connector.storage_read_log(cursor=args.cursor, max_bytes=args.max_bytes, timeout=args.timeout)


def request_storage_erase_log(connector, args):
    require_flag(args, "yes_really_erase_log", "storage erase-log requires --yes-really-erase-log")
    return connector.storage_erase_log(confirm_nonce=args.confirm_nonce, timeout=args.timeout)


def request_gpio_configure(connector, args):
    message = connector.hub.board.create_gpio_configure(pin=args.pin, direction=args.direction, pull=args.pull, initial_value=args.initial_value, force=args.force)
    return connector.send_request(message, timeout=args.timeout)


def request_gpio_read(connector, args):
    return connector.send_request(connector.hub.board.create_gpio_read(pin=args.pin, force=args.force), timeout=args.timeout)


def request_gpio_write(connector, args):
    return connector.send_request(connector.hub.board.create_gpio_write(pin=args.pin, value=args.value), timeout=args.timeout)


def request_adc_read(connector, args):
    return connector.send_request(connector.hub.board.create_adc_read(channel=args.channel, samples=args.samples), timeout=args.timeout)


def request_i2c_transfer(connector, args):
    message = connector.hub.board.create_i2c_transfer(address=args.address, write_data=args.write_data, read_length=args.read_length, repeated_start=args.repeated_start, frequency_hz=args.frequency_hz, force=args.force)
    return connector.send_request(message, timeout=args.timeout)


def request_spi_transfer(connector, args):
    message = connector.hub.board.create_spi_transfer(cs_pin=args.cs_pin, frequency_hz=args.frequency_hz, mode=args.mode, tx_data=args.tx_data, read_length=args.read_length, force=args.force)
    return connector.send_request(message, timeout=args.timeout)


def request_profile_get(connector, args):
    return connector.send_request(connector.hub.board.create_remote_profile_get(profile_id=args.profile_id), timeout=args.timeout)


def request_profile_set(connector, args):
    message = connector.hub.board.create_remote_profile_set(persist=args.persist)
    profile = message.message.board.remote_profile_set.profile
    profile.profile_id = args.profile_id
    profile.name = args.name
    profile.sensitivity = args.sensitivity
    profile.deadzone = args.deadzone
    profile.pointer_mode = args.pointer_mode
    profile.tilt_mode = args.tilt_mode
    return connector.send_request(message, timeout=args.timeout)


def request_pair_window(connector, args):
    return connector.start_pairing(duration_ms=args.duration_ms, timeout=args.timeout)


def request_hid_status(connector, args):
    return connector.get_hid_status(timeout=args.timeout)


def request_forget_bonds(connector, args):
    require_flag(args, "yes_really_clear_bonds", "forget requires --yes-really-clear-bonds")
    return connector.forget_bonds(confirm_nonce=args.confirm_nonce, timeout=args.timeout)


def request_pin_release(connector, args):
    require_flag(args, "yes_release_pin", "pin-release requires --yes-release-pin")
    message = connector.hub.board.create_release_pin(resource=args.resource, instance=args.instance)
    return connector.send_request(message, timeout=args.timeout)


SENSOR_ID_COLOR = 10
SENSOR_ID_PROXIMITY = 11
SENSOR_ID_GESTURE = 12


def request_apds_color(connector, args):
    return connector.read_sensor(SENSOR_ID_COLOR, timeout=args.timeout)


def request_apds_proximity(connector, args):
    return connector.read_sensor(SENSOR_ID_PROXIMITY, timeout=args.timeout)


def request_apds_gesture(connector, args):
    return connector.read_sensor(SENSOR_ID_GESTURE, timeout=args.timeout)


def request_apds_stream_color(connector, args):
    return connector.configure_stream(
        SENSOR_ID_COLOR, args.rate_millihz, timeout=args.timeout)


def request_apds_stream_proximity(connector, args):
    return connector.configure_stream(
        SENSOR_ID_PROXIMITY, args.rate_millihz, timeout=args.timeout)


def request_apds_profile(connector, args):
    return connector.get_input_state(timeout=args.timeout)


def add_common_io(parser):
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--json", action="store_true")


def add_leaf(subparsers, name, handler):
    parser = subparsers.add_parser(name)
    add_common_io(parser)
    parser.set_defaults(handler=handler)
    return parser


def build_parser():
    parser = argparse.ArgumentParser(prog="wboard")
    parser.add_argument("--interface", "-i", required=True)
    subcommands = parser.add_subparsers(dest="command", required=True)
    add_leaf(subcommands, "info", request_info)

    runtime = subcommands.add_parser("runtime").add_subparsers(dest="runtime_command", required=True)
    add_leaf(runtime, "config", request_runtime_config)
    runtime_mode = add_leaf(runtime, "mode", request_runtime_mode)
    runtime_mode.add_argument("mode", type=parse_int, choices=[1, 2])
    runtime_mode.add_argument("--persist", action="store_true")
    runtime_mode.add_argument("--reboot", action="store_true")
    runtime_pair = add_leaf(runtime, "open-pairing", request_runtime_open_pairing)
    runtime_pair.add_argument("--duration-ms", type=parse_int, required=True)
    runtime_clear = add_leaf(runtime, "clear-bonds", request_runtime_clear_bonds)
    runtime_clear.add_argument("--confirm-nonce", type=parse_int, required=True)
    runtime_clear.add_argument("--yes-really-clear-bonds", action="store_true")

    sensor = subcommands.add_parser("sensor").add_subparsers(dest="sensor_command", required=True)
    sensor_list = add_leaf(sensor, "list", request_sensor_list)
    sensor_list.add_argument("--cursor", type=parse_int, default=0)
    sensor_read = add_leaf(sensor, "read", request_sensor_read)
    sensor_read.add_argument("sensor_id", type=parse_int)

    stream = subcommands.add_parser("stream").add_subparsers(dest="stream_command", required=True)
    stream_start = add_leaf(stream, "start", request_stream_start)
    stream_start.add_argument("sensor_id", type=parse_int)
    stream_start.add_argument("rate_millihz", type=parse_int)
    stream_start.add_argument("--flags", type=parse_int, default=0)
    stream_stop = add_leaf(stream, "stop", request_stream_stop)
    stream_stop.add_argument("sensor_id", type=parse_int)

    calibration = subcommands.add_parser("calibration").add_subparsers(dest="calibration_command", required=True)
    calibration_run = add_leaf(calibration, "run", request_calibration_run)
    calibration_run.add_argument("sensor_id", type=parse_int)
    calibration_run.add_argument("--flags", type=parse_int, default=0)
    calibration_run.add_argument("--persist", action="store_true")
    calibration_get = add_leaf(calibration, "get", request_calibration_get)
    calibration_get.add_argument("sensor_id", type=parse_int)

    calibrate = subcommands.add_parser("calibrate").add_subparsers(dest="calibrate_command", required=True)
    calibrate_imu = add_leaf(calibrate, "imu", request_calibrate_imu)
    calibrate_imu.add_argument("--flags", type=parse_int, default=0)
    calibrate_imu.add_argument("--persist", action="store_true")
    calibrate_mag = add_leaf(calibrate, "mag", request_calibrate_mag)
    calibrate_mag.add_argument("--flags", type=parse_int, default=0)
    calibrate_mag.add_argument("--persist", action="store_true")

    hid = subcommands.add_parser("hid").add_subparsers(dest="hid_command", required=True)
    pair = add_leaf(hid, "pair", request_pair_window)
    pair.add_argument("--duration-ms", type=parse_int, required=True)
    hid_status = add_leaf(hid, "status", request_hid_status)
    hid_forget = add_leaf(hid, "forget", request_forget_bonds)
    hid_forget.add_argument("--confirm-nonce", type=parse_int, required=True)
    hid_forget.add_argument("--yes-really-clear-bonds", action="store_true")
    profile_get = add_leaf(hid, "profile-get", request_profile_get)
    profile_get.add_argument("profile_id", type=parse_int)
    profile_set = add_leaf(hid, "profile-set", request_profile_set)
    profile_set.add_argument("profile_id", type=parse_int)
    profile_set.add_argument("name")
    profile_set.add_argument("--sensitivity", type=parse_int, default=0)
    profile_set.add_argument("--deadzone", type=parse_int, default=0)
    profile_set.add_argument("--pointer-mode", action="store_true")
    profile_set.add_argument("--tilt-mode", action="store_true")
    profile_set.add_argument("--persist", action="store_true")

    audio = subcommands.add_parser("audio").add_subparsers(dest="audio_command", required=True)
    audio_configure = add_leaf(audio, "configure", request_audio_configure)
    audio_configure.add_argument("--enabled", action="store_true")
    audio_configure.add_argument("--sample-rate-hz", type=parse_int, default=16000)
    audio_configure.add_argument("--gain-db-x2", type=parse_int, default=40)
    audio_configure.add_argument("--flags", type=parse_int, default=0)
    raw_pcm = add_leaf(audio, "raw-pcm", request_raw_pcm)
    raw_pcm.add_argument("--duration-ms", type=parse_int, required=True)
    raw_pcm.add_argument("--chunk-size", type=parse_int, default=128)
    audio_metrics = add_leaf(audio, "metrics", request_audio_metrics)
    audio_metrics.add_argument("--count", type=parse_int, default=0)
    audio_metrics.add_argument("--timeout", type=float, default=5.0)

    output = subcommands.add_parser("output").add_subparsers(dest="output_command", required=True)
    output_set = add_leaf(output, "set", request_output_set)
    output_set.add_argument("target", type=parse_int)
    output_set.add_argument("value", type=parse_int)
    output_set.add_argument("--duration-ms", type=parse_int, default=0)
    output_set.add_argument("--force", action="store_true")
    output_stop = add_leaf(output, "stop", request_output_stop)
    output_stop.add_argument("target", type=parse_int)
    output_stop.add_argument("--force", action="store_true")
    output_buzzer = add_leaf(output, "buzzer", request_output_buzzer)
    output_buzzer.add_argument("frequency", type=parse_int)
    output_buzzer.add_argument("--duration-ms", type=parse_int, default=200)
    output_neopixel = add_leaf(output, "neopixel", request_output_neopixel)
    output_neopixel.add_argument("red", type=parse_int)
    output_neopixel.add_argument("green", type=parse_int)
    output_neopixel.add_argument("blue", type=parse_int)
    output_white = add_leaf(output, "white", request_output_white)
    output_white.add_argument("value", type=parse_int, choices=[0, 1])
    output_red = add_leaf(output, "red", request_output_red)
    output_red.add_argument("value", type=parse_int, choices=[0, 1])
    output_backlight = add_leaf(output, "backlight", request_output_backlight)
    output_backlight.add_argument("value", type=parse_int, choices=[0, 1])

    storage = subcommands.add_parser("storage").add_subparsers(dest="storage_command", required=True)
    add_leaf(storage, "info", request_storage_info)
    storage_adopt = add_leaf(storage, "adopt", request_storage_adopt)
    storage_adopt.add_argument("--confirm-nonce", type=parse_int, required=True)
    storage_adopt.add_argument("--force", action="store_true")
    storage_adopt.add_argument("--yes-really-adopt-and-erase", action="store_true")
    storage_read = add_leaf(storage, "read-log", request_storage_read_log)
    storage_read.add_argument("--cursor", type=parse_int, default=0)
    storage_read.add_argument("--max-bytes", type=parse_int, default=256)
    storage_erase = add_leaf(storage, "erase-log", request_storage_erase_log)
    storage_erase.add_argument("--confirm-nonce", type=parse_int, required=True)
    storage_erase.add_argument("--yes-really-erase-log", action="store_true")

    gpio = subcommands.add_parser("gpio").add_subparsers(dest="gpio_command", required=True)
    gpio_configure = add_leaf(gpio, "configure", request_gpio_configure)
    gpio_configure.add_argument("pin", type=parse_int)
    gpio_configure.add_argument("direction", type=parse_int)
    gpio_configure.add_argument("--pull", type=parse_int, default=1)
    gpio_configure.add_argument("--initial-value", action="store_true")
    gpio_configure.add_argument("--force", action="store_true")
    gpio_read = add_leaf(gpio, "read", request_gpio_read)
    gpio_read.add_argument("pin", type=parse_int)
    gpio_read.add_argument("--force", action="store_true")
    gpio_write = add_leaf(gpio, "write", request_gpio_write)
    gpio_write.add_argument("pin", type=parse_int)
    gpio_write.add_argument("value", type=parse_int)

    adc_read = add_leaf(subcommands, "adc", request_adc_read)
    adc_read.add_argument("channel", type=parse_int)
    adc_read.add_argument("--samples", type=parse_int, default=1)
    i2c = add_leaf(subcommands, "i2c", request_i2c_transfer)
    i2c.add_argument("address", type=parse_int)
    i2c.add_argument("--write-data", type=parse_hex, default=b"")
    i2c.add_argument("--read-length", type=parse_int, default=0)
    i2c.add_argument("--repeated-start", action="store_true")
    i2c.add_argument("--frequency-hz", type=parse_int, default=400000)
    i2c.add_argument("--force", action="store_true")
    spi = add_leaf(subcommands, "spi", request_spi_transfer)
    spi.add_argument("cs_pin", type=parse_int)
    spi.add_argument("--frequency-hz", type=parse_int, default=1000000)
    spi.add_argument("--mode", type=parse_int, default=1)
    spi.add_argument("--tx-data", type=parse_hex, default=b"")
    spi.add_argument("--read-length", type=parse_int, default=0)
    spi.add_argument("--force", action="store_true")

    input_cmd = subcommands.add_parser("input").add_subparsers(dest="input_command", required=True)
    add_leaf(input_cmd, "state", request_input_state)
    input_configure = add_leaf(input_cmd, "configure", request_input_configure)
    input_configure.add_argument("mode", type=parse_int)
    input_configure.add_argument("--flags", type=parse_int, default=0)
    input_configure.add_argument("--dwell-ms", type=parse_int, default=0)
    input_configure.add_argument("--deadzone", type=parse_int, default=0)
    input_configure.add_argument("--persist", action="store_true")

    pin_release = add_leaf(subcommands, "pin-release", request_pin_release)
    pin_release.add_argument("resource", type=parse_int)
    pin_release.add_argument("instance", type=parse_int)
    pin_release.add_argument("--yes-release-pin", action="store_true")

    apds = subcommands.add_parser("apds").add_subparsers(dest="apds_command", required=True)
    add_leaf(apds, "color", request_apds_color)
    add_leaf(apds, "proximity", request_apds_proximity)
    add_leaf(apds, "gesture", request_apds_gesture)
    add_leaf(apds, "profile", request_apds_profile)
    apds_stream_color = add_leaf(apds, "stream-color", request_apds_stream_color)
    apds_stream_color.add_argument("rate_millihz", type=parse_int)
    apds_stream_proximity = add_leaf(apds, "stream-proximity", request_apds_stream_proximity)
    apds_stream_proximity.add_argument("rate_millihz", type=parse_int)
    return parser


def run(args):
    from whad.board.connector import BoardConnector
    from whad.device import Device

    device = Device.create(args.interface)
    connector = BoardConnector(device)
    try:
        response = args.handler(connector, args)
        print_response(response)
    finally:
        connector.close()


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    run(args)


if __name__ == "__main__":
    main(sys.argv[1:])
