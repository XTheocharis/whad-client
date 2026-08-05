Expert I/O (edge connector)
==========================

.. contents:: :local:

The Board domain exposes the device's edge-connector pins as four resource
families: GPIO, I2C, SPI, and ADC. Each family is leased to the host on demand
through a token; the host releases the lease when it is done. The connector
abstracts the lease lifecycle into per-family methods.


Resource identifiers
--------------------

The connector exposes the resource families as class constants:

================================  ===========  ========================
Constant                         Value        Family
================================  ===========  ========================
``RESOURCE_GPIO_PIN``            1            digital GPIO
``RESOURCE_I2C_BUS``             2            shared I2C master
``RESOURCE_SPI_BUS``             3            shared SPI master
``RESOURCE_ADC_CHANNEL``         4            analog input
``RESOURCE_OUTPUT``              5            buzzer / LEDs / NeoPixel
``RESOURCE_STORAGE``             6            QSPI flash
================================  ===========  ========================


GPIO
----

GPIO access goes through
:func:`~whad.board.BoardConnector.i2c_transfer` siblings on the
:class:`whad.board.BoardConnector` (the firmware exposes ``GpioConfigure``,
``GpioRead``, ``GpioWrite`` as discrete Board commands). The connector wraps
them as low-level helpers; users typically drive GPIO through the ``wboard``
CLI or by sending the underlying hub messages directly.


I2C
---

:func:`whad.board.BoardConnector.i2c_transfer` performs a combined
write-then-read transaction on the shared I2C bus. Two convenience wrappers
split it for the common cases:

.. code-block:: python

    # Write two bytes to a device at address 0x50, no read-back.
    board.i2c_write(address=0x50, data=b"\x01\x02")

    # Read four bytes from register 0x00 of the same device.
    board.i2c_read(address=0x50, read_length=4)

For a register read (write the register address, repeated start, then read),
use the underlying method:

.. code-block:: python

    response = board.i2c_transfer(
        address=0x50,
        write_data=b"\x00",
        read_length=4,
        repeated_start=True,
        frequency_hz=400000,
    )
    print(response.read_data)


SPI
---

:func:`whad.board.BoardConnector.spi_transfer` performs a half-duplex or
full-duplex SPI transaction with chip-select asserted by the firmware on the
requested ``cs_pin``. Mode and frequency are configurable.

.. code-block:: python

    response = board.spi_transfer(
        cs_pin=10,
        frequency_hz=1_000_000,
        mode=1,                      # SPI_MODE_0
        tx_data=bytes.fromhex("deadbeef"),
        read_length=4,
    )
    print(response.read_data)


ADC
---

Analog reads go through the ``AdcRead`` Board command, which the ``wboard adc``
subcommand wraps. The Python connector does not yet expose a dedicated
``adc_read`` helper; the simplest path is to drive the underlying hub message:

.. code-block:: python

    message = board.hub.board.create_adc_read(channel=2)
    response = board.send_request(message)
    print(response.millivolts)


Releasing pins
--------------

When you are done with a leased resource, call
:func:`~whad.board.BoardConnector.release_pin` with the resource family and
the pin or channel identifier so the firmware can lease it again.

.. code-block:: python

    board.release_pin(resource=BoardConnector.RESOURCE_GPIO_PIN, instance=4)
