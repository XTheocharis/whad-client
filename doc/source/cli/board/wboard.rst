.. _whad-wboard:

wboard: Board domain tool
=========================

``wboard`` drives the *Board* domain of a WHAD-capable device. It exposes
on-board peripherals (sensors, storage, edge-connector I/O, outputs, runtime
management) as a single command tree, mirroring the
:class:`whad.board.BoardConnector` API.

The tool is built on plain ``argparse`` and does not subclass
:class:`whad.cli.app.CommandLineApp`. As a result it accepts a smaller set of
common options than the radio-specific CLIs and does not support shell-style
tool chaining.

Usage
-----

The general form is::

    wboard -i <interface> <subcommand> [subcommand options]

Every invocation requires ``--interface`` (``-i``). The interface follows the
same convention as the rest of WHAD: ``uart0``, ``hci0``, or a transport spec
such as ``uart:/dev/ttyUSB0``.

.. code-block:: text

    # wboard -i uart0 info
    [i] Connecting to device ...
    board_name: Adafruit CLUE
    hw_revision: nRF52840
    fw_version: 1.2.0
    sensor_count: 14
    active_runtime: RAW_WHAD (1)

Add ``--json`` to any subcommand to receive the raw protobuf response as
indented JSON instead of the default human-readable rendering:

.. code-block:: text

    # wboard -i uart0 info --json
    {
      "board": {
        "board_info": {
          "board_name": "Adafruit CLUE",
          "hw_revision": "nRF52840",
          ...
        }
      }
    }


Command-line options
--------------------

The following options are added by ``add_common_io`` to *every* ``wboard``
subcommand:

``-i, --interface <name>``
    Required. WHAD device interface (``uart0``, ``hci0``, ``uart:/dev/ttyUSB0``,
    ...).

``--timeout <seconds>``
    Per-request timeout in seconds (float). Defaults to ``2.0``. Streaming
    subcommands override the default but accept the same flag.

``--json``
    Emit the underlying protobuf message as indented JSON instead of the
    default human-readable rendering. Useful for scripting.


Supported commands
------------------

``wboard`` organises its subcommands into the following groups. Run
``wboard -i <interface> <group> --help`` to see the per-group options.


Board information
~~~~~~~~~~~~~~~~~

``info``
    Query the board name, hardware revision, firmware version, sensor count,
    and active runtime identifier.


Runtime management
~~~~~~~~~~~~~~~~~~

``runtime config``
    Read the current runtime configuration (active runtime, BLE flags,
    persistence state, bond count).

``runtime mode <1|2>``
    Switch the active runtime mode. ``1`` selects raw-WHAD, ``2`` selects
    BLE-HID. Switching triggers a watchdog reset; the device re-enumerates a
    few seconds later.

``runtime open-pairing [--duration-ms N]``
    Open a BLE pairing window for ``N`` milliseconds (default 30000). Only
    meaningful in BLE-HID mode.

``runtime clear-bonds --confirm-nonce N --yes-really-clear-bonds``
    Forget every stored BLE bond. The confirmation flag and nonce make the
    destructive intent explicit at the CLI layer.


Sensors
~~~~~~~

``sensor list``
    Walk the paginated sensor descriptor table.

``sensor read <id>``
    Read one sample from the given sensor id.


Streaming
~~~~~~~~~

``stream start <id> <rate_millihz>``
    Start a continuous stream for the given sensor at the given rate. The
    rate is expressed in millihertz (``104000`` means 104.0 Hz).

``stream stop <id>``
    Stop an active stream for the given sensor.


Calibration
~~~~~~~~~~~

``calibration run <id> [--persist]``
    Run a calibration procedure for the given sensor.

``calibration get <id>``
    Read the calibration currently stored on the device.

``calibrate imu`` / ``calibrate mag``
    Shortcuts for the IMU (sensor id 1) and magnetometer (sensor id 3)
    calibration procedures.


HID remote (BLE-HID mode)
~~~~~~~~~~~~~~~~~~~~~~~~~

``hid status``
    Report the BLE connection state and the number of stored bonds.

``hid pair [--duration-ms N]``
    Alias for ``runtime open-pairing``.

``hid forget --confirm-nonce N --yes-really-clear-bonds``
    Alias for ``runtime clear-bonds``.

``hid profile-get <id>``
    Read the configuration of HID profile ``id`` (1-4).

``hid profile-set <id> ...``
    Update an HID profile. See ``--help`` for the per-profile options.


Outputs
~~~~~~~

``output set <target> <value> [--duration-ms N] [--force]``
    Generic output setter. ``target`` is one of the integers exposed by
    ``BoardConnector`` (1=buzzer, 2=NeoPixel, 3=white LED, 4=red LED,
    5=backlight).

``output stop <target> [--force]``
    Stop the buzzer or turn off a previously set output.

``output buzzer <freq_hz> [--duration-ms N]``
    Convenience wrapper that targets the buzzer (``target=1``).

``output neopixel <r> <g> <b>``
    Set the NeoPixel to the given RGB triple.

``output white <0|1>`` / ``output red <0|1>`` / ``output backlight <0|1>``
    Toggle the white LED, red LED, or TFT backlight.


Storage
~~~~~~~

``storage info``
    Report the QSPI storage adoption state, capacity, and log record count.

``storage adopt --confirm-nonce N --yes-really-adopt-and-erase``
    Adopt the QSPI storage. Erases the chip and writes a journal header.

``storage read-log [--cursor N] [--max-bytes N]``
    Read one chunk of the journal log. Walks the log when called repeatedly
    with the cursor returned by the previous call.

``storage erase-log --confirm-nonce N --yes-really-erase-log``
    Begin an asynchronous log-erase transaction.


Expert I/O
~~~~~~~~~~

``gpio configure <pin> <direction>``
    Configure a GPIO pin for the given direction (``2`` for output).

``gpio read <pin>``
    Read the digital level of a GPIO pin.

``gpio write <pin> <value>``
    Drive a GPIO pin to the given level.

``adc <channel>``
    Read one sample from the given ADC channel.

``i2c <address> [--write-data HEX] [--read-length N] [--frequency-hz HZ]``
    Perform an I2C transfer with the device at ``address``.

``spi <cs_pin> [--frequency-hz HZ] [--mode M] [--tx-data HEX] [--read-length N]``
    Perform an SPI transfer with chip-select on ``cs_pin``.


Pin lease management
~~~~~~~~~~~~~~~~~~~~

``pin-release <resource> <instance> --yes-release-pin``
    Release a previously leased pin or channel. ``resource`` is the integer
    identifier exposed by ``BoardConnector`` (1=GPIO pin, 2=I2C bus, 3=SPI
    bus, 4=ADC channel).


Input state
~~~~~~~~~~~

``input state``
    Read the current motion-input state (tilt, air-mouse, deadzone).

``input configure [--mode M] [--dwell-ms N] [--deadzone N] [--persist]``
    Configure the motion-input engine.


APDS9960 shortcuts
~~~~~~~~~~~~~~~~~~

``apds color`` / ``apds proximity`` / ``apds gesture``
    Read one sample from the APDS9960 (sensor id 10, 11, or 12).

``apds profile``
    Read the APDS9960 integration profile.

``apds stream-color <rate_millihz>`` / ``apds stream-proximity <rate_millihz>``
    Start a continuous stream for the color or proximity sensor.


Audio
~~~~~

``audio configure [--sample-rate-hz N] [--gain-db-x2 N] [--enabled 0|1]``
    Configure the PDM microphone.

``audio raw-pcm <duration_ms> [--chunk-size N]``
    Stream raw PCM samples from the microphone for ``duration_ms``
    milliseconds. Output is hex by default; pass ``--json`` for a structured
    envelope.

``audio metrics``
    Subscribe to the audio-level sensor (id 13) and print rolling metrics.
