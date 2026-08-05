Getting started
===============

.. contents:: :local:

The *Board* domain is the most recent addition to the WHAD protocol. Unlike the
radio-focused domains (BLE, 802.15.4, ESB, Unifying, PHY), the Board domain
exposes the on-board peripherals of a WHAD-capable device: environmental and
motion sensors, QSPI storage, edge-connector I/O (GPIO, I2C, SPI, ADC), outputs
(buzzer, LEDs, NeoPixel), and runtime management. It does not carry radio
packets and for that reason has no *Scapy* layer. Messages flow through
``on_domain_msg`` instead of ``on_packet``.

A typical use case is the *Adafruit CLUE* (nRF52840) running the ButteRFly
firmware, which advertises 14 sensors alongside the standard radio domains. Any
WHAD device that implements the Board domain can be driven the same way.


Connecting to a Board device
----------------------------

The :class:`whad.board.connector.base.BoardConnector` is the entry point. It
behaves like every other WHAD connector: pass it a :class:`whad.device.Device`
wrapping the underlying transport.

.. code-block:: python

    from whad.device import WhadDevice
    from whad.board import BoardConnector

    device = WhadDevice.create('uart:/dev/ttyUSB0')
    board = BoardConnector(device)

    # The connector opens the device, performs discovery, and verifies that
    # the Board domain is supported. If it isn't, UnsupportedDomain is raised.

The alias :class:`whad.board.Board` is available as a shortcut:


.. code-block:: python

    from whad.board import Board

    board = Board(device)


Reading board information
-------------------------

The :func:`whad.board.BoardConnector.get_board_info` method returns a
``BoardInfo`` response with the board name, hardware revision, firmware version,
sensor count, and active runtime identifier.

.. code-block:: python

    info = board.get_board_info()
    print(info.board_name)        # e.g. "Adafruit CLUE"
    print(info.sensor_count)      # e.g. 14
    print(info.active_runtime)    # 1 = raw-WHAD, 2 = BLE-HID


Enumerating sensors
-------------------

The :func:`whad.board.BoardConnector.list_sensors` method returns a
``SensorDescriptor`` for each sensor the board exposes. The Board protocol uses
cursor-based pagination: the response carries a ``cursor`` field that the next
call passes back to fetch the next descriptor. A cursor of ``0`` starts from the
beginning; when the response reports ``eof=True`` there are no more sensors.

.. code-block:: python

    cursor = 0
    while True:
        descriptor = board.list_sensors(cursor=cursor)
        print(descriptor.sensor_id, descriptor.name)
        if descriptor.eof:
            break
        cursor = descriptor.cursor


Reading sensor data
-------------------

To pull a single sample, call :func:`whad.board.BoardConnector.read_sensor`
with the sensor identifier. The returned ``SensorSample`` carries the raw
values, the sensor identifier, and a timestamp. The semantic of each value
field depends on the sensor and is documented in :doc:`sensors`.

.. code-block:: python

    sample = board.read_sensor(sensor_id=1)   # acceleration
    print(sample.values)

For continuous acquisition, see :doc:`sensors` for the streaming API
(:func:`~whad.board.BoardConnector.configure_stream` and
:func:`~whad.board.BoardConnector.stop_stream`).

When you are done, close the connector to release the device:

.. code-block:: python

    board.close()
