Runtime configuration
=====================

.. contents:: :local:

WHAD devices that implement the Board domain can run in more than one *runtime
mode*. The Adafruit CLUE running ButteRFly exposes two mutually exclusive
modes:

* **Raw-WHAD** (``active_runtime=1``, the default). The radio subsystem is
  driven directly by the firmware and exposes BLE, 802.15.4, ESB, Unifying,
  and PHY domains alongside the Board domain.
* **BLE-HID** (``active_runtime=2``). The radio is owned by a SoftDevice-based
  BLE HID remote control. Only the Board domain stays reachable over USB.

Switching modes requires a system reset; the device cannot serve both at the
same time.


Reading the runtime configuration
---------------------------------

The Board domain does not yet expose a dedicated wrapper for
``GetRuntimeConfig`` on :class:`whad.board.BoardConnector`. Construct the
request through the hub factory and send it explicitly:

.. code-block:: python

    from whad.device import WhadDevice
    from whad.board import BoardConnector

    device = WhadDevice.create('uart:/dev/ttyUSB0')
    board = BoardConnector(device)

    message = board.hub.board.create_get_runtime_config()
    response = board.send_request(message)

    print(response.active_runtime)             # 1 = raw-WHAD, 2 = BLE-HID
    print(response.ble_pairable)               # True when the BLE runtime is up
    print(response.persistence_available)      # True when QSPI storage is adopted
    print(response.bond_count)                 # number of stored BLE bonds

The response is a ``RuntimeConfig`` message that bundles the active runtime,
the BLE-HID availability flags, the persistence status, and the bond count.


Switching runtime mode
----------------------

Switching is done with the ``SetRuntimeMode`` request. The wrapper
:func:`whad.board.BoardConnector.start_pairing` and
:func:`~whad.board.BoardConnector.forget_bonds` use the related
``SetRuntimeConfig`` request, which is the proper path for runtime-related
side effects while staying in the same mode.

.. warning::

    Mode switching triggers a watchdog reset on the device. The USB CDC
    connection drops and re-enumerates a few seconds later. The connector's
    pending-request table is invalidated by the reset; create a fresh
    :class:`~whad.board.BoardConnector` after the device reappears.


Persisting side effects
-----------------------

The ``SetRuntimeConfig`` request accepts a ``persist`` flag. When the storage
is adopted (see :doc:`storage`), the firmware writes the new configuration to
the QSPI journal so it survives reboot. Two convenience wrappers cover the
common operations:

* :func:`~whad.board.BoardConnector.start_pairing` opens a BLE pairing window
  for a configurable duration in milliseconds.
* :func:`~whad.board.BoardConnector.forget_bonds` clears all stored bonds. It
  requires a ``confirm_nonce`` argument to make the destructive intent
  explicit.

Both methods are only meaningful in BLE-HID mode; in raw-WHAD mode they return
``NOT_IMPLEMENTED``.
