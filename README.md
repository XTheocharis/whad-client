# WHAD: Wireless HAcking Devices

[![Tests](https://github.com/virtualabs/whad-client/actions/workflows/tests.yml/badge.svg)](https://github.com/virtualabs/whad-client/actions/workflows/tests.yml)

This framework provides a set of command-line tools to play with/hack/explore
wireless protocols and devices as well as a library to create powerful wireless
tools to use with hardware devices running a compatible firmware.

## Installation

Installation is pretty straightforward with ``pip``:

```
pip install whad
```

## Online documentation

Project documentation is [available on ReadTheDocs](https://whad.readthedocs.io/en/stable/).

## Running unit tests

You can run unit tests locally for the default python version using:
```
pytest
```

You can run unit tests for every supported python version using:
```
tox
```

(You need to install Python interpreters from 3.9 to 3.13 included to run tox).
The tests are automatically run by github actions when something is pushed to main branch or when a pull request is merged.

---

## What's different on the `clue` branch

This is the `XTheocharis/whad-client` fork (branch `clue`) tracking `upstream/whad-team/whad-client#main`. The branch adds an **8th WHAD domain (Board)** end-to-end and two Linux-7.1.5 `cdc_acm` compatibility fixes for the ButteRFly dongle.

### Board domain package — `whad/hub/board/` (NEW, 5 files, 644L)
Hand-written wrappers around the generated `whad/protocol/board/board_pb2.py`. Every class is `@pb_bind`-registered into the `BoardDomain` `Registry` so `BoardDomain.parse(version, msg)` can dispatch by oneof name.
- `common.py` (58L) — `BoardMessage` base, 5 exceptions (`BoardConnectorError`, `BoardPendingRequestFull`, `BoardDuplicateRequest`, `BoardRequestTimeout`, `BoardEventQueueFull`), `PendingRequest` queue.
- `domain.py` (145L) — `BoardDomain(Registry)` factory + `Commands` enum (28 values 0x00-0x1B) + 26 `create_*` convenience methods.
- `events.py` (78L) — 6 unsolicited event wrappers: `SensorSample`, `AudioChunk`, `InputEvent`, `GestureEvent`, `LogChunk`, `BoardStatus`.
- `requests.py` (235L) — 28 request wrappers (one per outbound command).
- `responses.py` (158L) — 15 response wrappers.

### Board connector — `whad/board/connector/base.py` (NEW, 441L)
`class BoardConnector(Connector)` with `domain = "board"` (alias `Board`). Adds **request/response multiplexing** not in the base `Connector`:
- 32-bit `request_id` allocator (wraps at 0xFFFFFFFF, never returns 0). `request_id==0` ⇒ unsolicited event.
- Bounded queues: `MAX_PENDING_REQUESTS=8`, `MAX_RESPONSES_PER_REQUEST=8`, `MAX_EVENTS=32`.
- Terminal detection: `BoardCommandResult.terminal` truthy, `BoardStatus.terminal` truthy, `audio_chunk`/`log_chunk` with `eof or result!=0`, or `message_name in TERMINAL_MESSAGE_NAMES` frozenset (15 names).
- ~40 high-level command methods: `get_board_info`, `list_sensors`, `read_sensor`, `configure_stream`, `calibrate`, `set_buzzer`, `set_neopixel`, `i2c_transfer`, `spi_transfer`, `storage_info`, `storage_adopt`, `storage_read_log_all`, `set_runtime_mode`, `start_pairing`, `forget_bonds`, `raw_pcm_diagnostics`, etc.
- Constants: `OUTPUT_TARGET_*` (buzzer/neopixel/white_led/red_led/backlight), `RESOURCE_*` (gpio/i2c/spi/adc/output/storage), `SENSOR_ID_COLOR/PROXIMITY/GESTURE`.

### Board CLI — `whad/tools/wboard.py` (NEW, 465L)
Plain `argparse` — the only whad CLI that does NOT subclass `CommandLineApp` (Board has no Source/Sink/Pipe composition). 16 command groups, ~50 leaves: `info`, `runtime {config,mode,open-pairing,clear-bonds}`, `sensor {list,read}`, `stream {start,stop}`, `calibration {run,get}`, `calibrate {imu,mag}`, `hid {pair,status,forget,profile-get,profile-set}`, `audio {configure,raw-pcm,metrics}`, `output {set,stop,buzzer,neopixel,white,red,backlight}`, `storage {info,adopt,read-log,erase-log}`, `gpio {configure,read,write}`, `adc`, `i2c`, `spi`, `input {state,configure}`, `pin-release`, `apds {color,proximity,gesture,profile,stream-color,stream-proximity}`.

Pattern: `add_common_io(parser)` adds `--timeout`/`--json`; `add_leaf(subparsers, name, handler)` wraps both + sets handler. Destructive ops gated by `require_flag()` (`--yes-really-clear-bonds`, `--yes-really-adopt-and-erase`, `--yes-really-erase-log`, `--yes-release-pin`).

### Discovery / hub integration
- `whad/hub/__init__.py` — `Domain` StrEnum gains `BOARD = 'board'`; new `.board` property; `load('board')` factory branch. `convert_packet` does NOT include Board (no scapy layer).
- `whad/hub/discovery/__init__.py` — `Domain.Board = 0x0C000000` + four new `Capability` bits (`Read=0x100`, `Write=0x200`, `Stream=0x400`, `Store=0x800`).
- `whad/tools/whadup.py` — hardcoded `DOMAINS`/`CAPABILITIES`/`COMMANDS` dicts gain Board entries; capability loop widened from bit 23 to bit 31 for headroom.

### Linux-7.1.5 cdc_acm compatibility fixes
- `whad/_termios_patch.py` (NEW, 39L) — monkey-patches `termios.tcgetattr/tcsetattr/tcflush` to swallow `(termios.error, OSError)`. Returns a fake but valid termios list (`B115200|CS8|CREAD|CLOCAL`, raw lflag) on `tcgetattr` failure. Imported in `whad/__init__.py` BEFORE pyserial.
- `whad/device/uart.py` — defensive `_termios_patch` re-import + pyusb `SET_CONTROL_LINE_STATE` control transfer (bmRequestType=0x21, bRequest=0x22, wValue=0x0003 = DTR|RTS) issued before `Serial()` open on CDC ACM devices. Reason: Linux 7.1.5 `cdc_acm` doesn't send `SET_CONTROL_LINE_STATE` on tty open, and the nRF52 firmware rejects RX without DTR. Falls back to plain `Serial()` on any error.

### Tests (NEW, 8 files, 1881L, 79 cases — all PASS in 30s)
- `tests/protocol/board/test_board_factory.py` (43L) — domain/capability enum registration, request/response factory round-trip.
- `tests/board/test_board_connector.py` (74L) — domain attr + zero-id event vs nonzero-id response separation.
- `tests/board/test_base_client_compat.py` (149L) — Board coexists with BLE/ESB/etc, capability bits don't bleed, `UnsupportedDomain` on radio-only device.
- `tests/board/test_board_integration.py` (556L) — `ClueMockDevice` emulating 20 commands, correlated responses, set_runtime_mode/config, HID pairing/bonds, interleaved events.
- `tests/board/test_motion_integration.py` (318L) — IMU/mag/air_mouse sensors (1-5,14), cursor pagination, rate clamping, calibrate/get_calibration flows.
- `tests/board/test_apds_integration.py` (263L) — APDS9960 color/proximity/gesture (10/11/12), descriptor shapes, stream clamp.
- `tests/board/test_board_output.py` (261L) — buzzer/neopixel/LED/backlight targets, RGB packing, NO OUTPUT_TARGET_AUDIO lock, wboard argparse.
- `tests/board/test_storage_persistence.py` (217L) — QSPI adopt/read/erase lifecycle, nonce enforcement, volatile-cal-without-adoption lock.

All use `whad.device.mock.MockDevice` + `@MockDevice.route(RequestClass)` decorator — pure Python, no hardware required.

### Other
- `pyproject.toml` — `protobuf>=6.30` → `>=7.35.1` (major bump, required by regenerated proto). New script entry: `wboard = "whad.tools.wboard:main"`.
- `.gitignore` — adds `*.pyc` + `AGENTS.md`.

### Notes
- `whadup` shows Board alongside the radio domains. Board has no scapy layer — reached via `wboard` CLI or `BoardConnector` directly.
- After every `wboard`/`whadup` invocation, raw-WHAD firmware resets on CDC close. Wait ~3-4s for re-enumeration before the next command.
- No `examples/board/` directory yet (every other domain has examples). Good first-issue candidate.

See workspace `README.md` for the integrated 4-repo picture and `TODO.md` for outstanding work.
