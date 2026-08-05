Release notes for version 1.2.17
===============================

Bugfixes
--------

- Fixed undefined `data` variable replaced with `payload` in `TCPSocketDevice.write()` (issue #360)

Important changes
-----------------

### CLUES database migrated to latest version

The bundled CLUES database has been migrated to its latest version. The
database structure has been modified in this migration, consumers of the
CLUES API must verify their integration against the new schema.


Release notes for version 1.2.16
===============================

Bugfixes
--------

- Fixed `is_access_address_valid()`
- Fixed `UnicodeDecodeError` when decoding BLE device name
- Fixed incorrect RF channel computation in BLE packet metadata generation
- Fixed a bug in WHAD's `UUID` class
- Fixed Wireshark issues in `wble-central` and a BLE profile discovery bug in GATT
- Fixed BLE active connection sniffing
- Fixed type annotations to make them compatible with Python <= 3.10

New features
------------

### PCAP overwrite

`PcapWriterMonitor` can now overwrite existing PCAP files.

### Improved connection synchronization output

`wsniff` now provides improved output during connection synchronization.

Important changes
-----------------

### Tool chaining

This release introduces an argument to disable tool chaining, then removes the
`--disable-chaining` option (it was a duplicate of `--force-stdout`).
The `--force-stdout` option (introduced in 1.2.15) remains the supported way
to force dual stdout/chaining output.


Release notes for version 1.2.15
===============================

Bugfixes
--------

- Fixed long read GATT operation in `wble-central`
- Fixed BLE encryption issue caused by `_on_whad_ble_encryption()` being incorrectly renamed to `_1le_encryption()`
- Fixed a bug in the cryptobox unit test
- Fixed a crash in WHAD's BLE analyzer class used by `wanalyze`
- Fixed some typos in the `address` field used for debugging

New features
------------

### BLE pairing with raw PDU devices

Added tracing and an attempted fix for BLE pairing with devices supporting raw
BLE PDUs. WHAD's BLE stack now checks for raw PDU injection support in
`send_ctrl_pdu()` (control PDUs may be sent during pairing) and excludes HCI
from the existing control PDU sending checks.

### Encryption handling

Encryption enabling has been moved to `on_start_enc_req` to allow normal
processing of `ll_start_enc_rsp`.

Important changes
-----------------

### `--stdout` renamed to `--force-stdout`

The `--stdout` option has been renamed to `--force-stdout` for command-line
applications providing a dual (stdout/chaining) output, to remove the
ambiguity with the implicit stdout output of source tools. Documentation has
been updated accordingly.

### Tool chaining can be disabled

A new command-line application class has been added to allow the tool chaining
feature to be disabled by the user.


Release notes for version 1.2.14
===============================

Bugfixes
--------

- Fixed an error in `wsniff` when the target PCAP file already exists
- Fixed a bug when `Central` cannot read a descriptor value (sometimes seen with some weird devices; the descriptor is now considered as `00 00`)
- Fixed a regression in BLE characteristic notification/indication subscription

New features
------------

### PHY sniffing example

Added an example for `wsniff`'s PHY domain `--sync-word` option.

Improvements
------------

- Added a warning when the packet size set for sniffing is rejected by hardware
- Updated error messages


Release notes for version 1.2.13
===============================

Bugfixes
--------

- Fixed `profile` command to avoid stall
- Fixed a bug in GATT read long procedure (`ReadBlobRequest` was used to read the first part instead of a `ReadRequest`)
- `wble-central`'s `read` command now forces the read long procedure
- Renamed `ESB.sniff()` to `ESB.start_sniff()` to fix a regression in ESB's `Sniffer` connector
- Fixed a bug in ESB injector (`PTX` was incorrectly imported from `whad.esb.base` instead of `whad.esb.ptx`)

New features
------------

### Connection MTU retrieval

Added a method to retrieve the host's current connection MTU.


Release notes for versions 1.2.12
=================================

Bugfixes
--------

- Fixed HID key codes for BE keymap
- Fixed right-hand side ALT,SHIFT and CTRL key
- Fixed interactive shell prompt (missing whitespace before command)
- Fixed a bug in `wble-central` that caused a crash when reading a characteristic with an invalid offset
- Fixed connection attempt cancelation in HCI virtual device (BLE-related)
- Fixed a regression in `wble-connect` and `wble-spawn`
- Fixed a bug in WHAD's `Device` class that made the associated device index goes off
- Fixed multiple bugs in WHAD's BLE stack

New features
------------

### Bluetooth Low Energy Central API has been improved

In previous versions, once a connection to a target device established (an instance of `PeripheralDevice`), accessing a characteristic from 
a service was done as follows:

```python
my_char = remote_device.get_characteristic(UUID('1800'), UUID('2A00'))
if my_char is not None:
    print("Characteristic 2A00 has been found !")
else:
    print("No characteristic 2A00 found.")
```

This syntax is still supported to avoid a breaking change (and will be deprecated in the future), but
version 1.2.12 introduces new methods to get a simpler and more concise syntax:

```python
my_char = remote_device.char('2A00', '1800')
if my_char is not None:
    print("Characteristic 2A00 has been found !")
else:
    print("No characteristic 2A00 found.")
```

The new `char()` method has been designed to be really flexible and accepts UUIDs as strings or `UUID`
objects, with the service UUID (the second parameter in the example above, `1800`) being optional. In fact,
very few devices use identical characteristics' UUIDs in two or more different services. A shorter form
of the previous code could be:

```python
my_char = remote_device.char('2A00')
if my_char is not None:
    print("Characteristic 2A00 has been found !")
else:
    print("No characteristic 2A00 found.")
```

A similar change has been made to provide the `service()` method that now accepts the requested UUID as a string
or an instance of `UUID`:

```python
my_service = remote_device.service('1800')
```

### Bluetooth Low Energy standard services

The Bluetooth specification defines a set of _standard services_ with for each of them a set of associated mandatory
and optional characteristics, like the _Battery Service_ or the _Heart Rate Service_. Starting from version 1.2.12,
we added a feature to make interaction with such services easier:

```python
from whad.device import Device
from whad.ble import Central, UUID, BatteryService
from whad.ble.exceptions import PeripheralNotFound

# We assign a BLE central role to our HCI adapter
central = Central(Device.create("hci0"))

# Target not connected
target = None

try:
    # Connect to remote device and discover services and characteristics
    target = central.connect("00:11:22:33:44:55", random=True)
    target.discover()

    # Check the device exposes a Battery service, queries it and read
    # the battery's level as a percentage
    if target.has(BatteryService):
        battery = target.query(BatteryService)
        print(f"Battery level: {battery.percentage}%")
    else:
        print("Battery service is not supported by this device.")

    # Closing connection
    target.disconnect()

# Handle connection error
except PeripheralNotFound:
    print("Target device not found.")
```

To check if a given standard service is supported by a device (i.e. if it provides at least the associated GATT
service and defined mandatory characteristics), we simply use the `has()` method:

```python
    if target.has(BatteryService):
        # continue with target device
    else:
        # service is not supported
```

This method returns `True` if the requested service is supported. If so, we can retrieve an instance of this standard
service tied to our remote device and access some of its properties, like for instance the `percentage` property of
`BatteryService`:

```python
    # Check the device exposes a Battery service, queries it and read
    # the battery's level as a percentage
    if target.has(BatteryService):
        battery = target.query(BatteryService)
        print(f"Battery level: {battery.percentage}%")
    else:
        print("Battery service is not supported by this device.")
```

We provide the following default standard services:

- Battery Service
- Heart Rate Service
- Device Information Service

More standard services are expected to be implemented in the future, feel free to contribute and send us a pull request
to add more services! See documentation and code for implementation details.


Release notes for version 1.2.11
================================

Bugfixes
--------

- Logitech Unifying HID decoding has been improved and some related bugs fixed
- Global loading and processing time of the whole framework has been improved through lazy loading and other optimizations
- BLE sniffer and scanner connectors have been improved to support Python's `with` statement
- `wanalyze` documentation has been updated to reflect recently added options (`--set`)

New features
------------

This section details the new features introduced in version 1.2.11.

### Bluetooth Low Energy scanner and sniffer now supports contextual managers

Starting from version 1.2.11, Bluetooth Low Energy `Scanner` and `Sniffer` connectors
support Python's contextual managers through the use of a `with` statement. When used
in a `with` statement, these connectors handle transparently the hardware they are
associated with by automatically configuring, starting and stopping the associated
mode.

Scanning for BLE devices is now pretty easy to do, and more readable:

```python
from whad.device import Device
from whad.ble import Scanner

with Scanner(Device.create("hci0")) as scanner:
    for device in scanner.discover_devices():
        print(device)
```

### New IEEE 802.15.4 DLTs supported by wplay

Previous versions were only able to read PCAP files containing IEEE 802.15.4 frames stored
using the `LINKTYPE_IEEE802_15_4_TAP` format (type 283), this version adds support of the following
link types:

- `LINKTYPE_IEEE802_15_4_LINUX` (191)
- `LINKTYPE_IEEE802_15_4_WITHFCS` (195)
- `LINKTYPE_IEEE802_15_4_NONASK_PHY` (215)
- `LINKTYPE_IEEE802_15_4_NOFCS` (230)

### Improved performance

Version 1.2.11 also improves performance of the whole framework. We identified some bottlenecks
that led the framework to take seconds to completely load and modified the way it works to
significantly speed up its loading time. Its post-execution cleanup code has also been
improved to reduce the latency observed with most command-line tools when they were terminating.


Important changes
-----------------

Some changes made in this version introduce impact the way some components behave and the
data they consume or produce. This section provide a comprehensive overview of those major
modifications and their impact on scripts or applications that use them.

### HID ALT key

The Logitech Unifying HID converter component used by the `keystroke` traffic analyzer in `wanalyze`
has been updated to differentiate both left-hand side and right-hand side `ALT` keys, now returning
`LALT` as the textual description of the left-hand side `ALT` key and `RALT` for the right-hand side
`ALT` key instead of the single `ALT` text it previously returned for both. This may break scripts
or applications that rely on the previous `ALT` textual representation of those keys and they shall
be modified to handle these two new names.

### WHAD scapy layers

Previous versions of WHAD automatically loaded a set of custom *Scapy* layers for every supported
protocol, impacting the framework loading time. Starting from version 1.2.11, WHAD now relies on
lazy loading through its *protocol hub* component to load those layers whenever it is required,
optimizing the loading time and providing a smoother experience.

Applications or scripts that rely on these layers without WHAD's *protocol hub* need to explicitely
load these layers instead of simply importing all of them by using a ``from whad.scapy.layers import *``
statement. For instance, an application requiring WHAD's custom layers for Bluetooth Low Energy
shall now import the corresponding layers:

```python
from whad.scapy.layers.bluetooth import *
```

### `WhadDevice` renamed to `Device`

When accessing a compatible hardware with WHAD, previous versions used the `WhadDevice` class
to retrieve an object representing a specific interface:

```python
from whad.device import WhadDevice

dev = WhadDevice.create("uart0")
```

The `WhadDevice` class has been renamed to `Device` for simplicity, but the previous class is
kept for compatibility. The recommended way to access WHAD hardware interfaces is the following:

```python
from whad.device import Device

dev = Device.create("uart0")
```

The `WhadDevice` class will be deprecated in a future version, and is planned to be later removed.
When deprecated, the framework will display a warning message whenever this class is used to warn
about the upcoming removal. No planning has been defined yet for this deprecation and future removal,
but we will communicate about it when one had been decided.


