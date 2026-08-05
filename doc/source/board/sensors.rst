Sensors
=======

.. contents:: :local:

The Board domain exposes a list of *sensors* identified by a small integer
``sensor_id``. Each sensor has a fixed ``SensorDescriptor`` (name, unit,
component count, axis labels) and produces ``SensorSample`` values that match
that descriptor. The descriptor list is paginated; the sample stream is
multiplexed onto the same request_id-based reply channel used by every other
Board command.


Sensor identifiers
------------------

The Adafruit CLUE running ButteRFly exposes the following sensors. Other boards
may expose a different subset and use different identifiers; always enumerate
with :func:`~whad.board.BoardConnector.list_sensors` before relying on a
specific sensor id.

========== ============================= ================ =============================
ID         Sensor                        Unit             Components
========== ============================= ================ =============================
1          Acceleration                  mg               X, Y, Z (LSM6DS33)
2          Gyroscope                     mdps             X, Y, Z
3          Magnetic                      milligauss       X, Y, Z (LIS3MDL)
4          Quaternion                    Q30              W, X, Y, Z (Madgwick fusion)
5          Orientation                   millidegrees     yaw, pitch, roll
6          Pressure                      Pa               BMP280
7          BMP280 temperature            centi°C
8          Humidity                      centi%RH         SHT31-D
9          SHT31 temperature             centi°C
10         Color                         counts           R, G, B, Clear (APDS9960)
11         Proximity                     0–255            APDS9960
12         Gesture                       enum             UP/DOWN/LEFT/RIGHT/NEAR/FAR
13         Audio level                   dBFS × 1000      PDM microphone
14         Air mouse                     counts           dX, dY, dWheel, buttons
========== ============================= ================ =============================


Listing sensors
---------------

:func:`whad.board.BoardConnector.list_sensors` returns one ``SensorDescriptor``
per call. The protocol is cursor-based: pass the cursor returned by the previous
call to fetch the next descriptor. ``eof=True`` means the list is exhausted.

.. code-block:: python

    cursor = 0
    while True:
        descriptor = board.list_sensors(cursor=cursor)
        print(descriptor.sensor_id, descriptor.name, descriptor.unit)
        if descriptor.eof:
            break
        cursor = descriptor.cursor


Reading a single sample
-----------------------

:func:`whad.board.BoardConnector.read_sensor` returns one ``SensorSample``
for the requested sensor id.

.. code-block:: python

    sample = board.read_sensor(sensor_id=1)   # acceleration
    print(sample.sensor_id, sample.values, sample.timestamp)


Streaming sensor data
---------------------

Continuous acquisition uses
:func:`whad.board.BoardConnector.configure_stream`. Pass the sensor id, the
desired rate in millihertz (so 104000 means 104.0 Hz), and optional flags. The
device then emits ``SensorSample`` events on its event queue; consume them with
:func:`~whad.board.BoardConnector.next_event` or the
:func:`~whad.board.BoardConnector.motion_samples` generator.

.. code-block:: python

    board.configure_stream(sensor_id=1, rate_millihz=104000)   # 104 Hz

    for sample in board.motion_samples(sensor_id=1):
        print(sample.values)

To stop a stream, call :func:`whad.board.BoardConnector.stop_stream`:

.. code-block:: python

    board.stop_stream(sensor_id=1)


Calibration
-----------

Some sensors (IMU, magnetometer) benefit from calibration. The Board domain
exposes two methods:

* :func:`~whad.board.BoardConnector.calibrate` runs the calibration procedure
  for a sensor id and returns the resulting ``Calibration`` payload.
* :func:`~whad.board.BoardConnector.get_calibration` returns the calibration
  currently stored on the device without running a new procedure.

Two convenience wrappers target the most common sensors:

.. code-block:: python

    board.calibrate_imu(persist=True)
    board.calibrate_mag(persist=True)

When ``persist=True``, the calibration is written to the QSPI journal so it
survives a reboot. See :doc:`storage` for the underlying storage lifecycle.


Color, proximity, gesture shortcuts
-----------------------------------

The APDS9960 is exposed as three sensors (ids 10, 11, 12). The connector
ships with convenience methods for the common case:

.. code-block:: python

    color       = board.read_color()
    proximity   = board.read_proximity()
    gesture     = board.read_gesture()

Streaming variants are also available:

.. code-block:: python

    board.stream_color(rate_millihz=50000)
    board.stream_proximity(rate_millihz=50000)
