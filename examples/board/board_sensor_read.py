from whad.device import Device
from whad.board.connector.base import BoardConnector
import sys

if len(sys.argv) >= 2:
    interface = sys.argv[1]
    # Create the Board connector & the WHAD device
    connector = BoardConnector(Device.create(interface))

    # List available sensors (paginated: one descriptor per response)
    print("[i] Sensors:")
    cursor = 0
    while True:
        response = connector.list_sensors(cursor=cursor)
        if response.message.board.sensor_descriptor.HasField("descriptor"):
            desc = response.descriptor
            print(" + ID %d: %s (%s)" % (desc.sensor_id, desc.name, desc.unit))
        if response.eof or response.next_cursor == 0:
            break
        cursor = response.next_cursor

    # Read a single sensor if sensor ID is given
    if len(sys.argv) >= 3:
        sensor_id = int(sys.argv[2])
        sample = connector.read_sensor(sensor_id)
        print("[i] Sensor %d sample: %s" % (sensor_id, sample.values))

    connector.close()
else:
    print("Usage: ", sys.argv[0]+" <interface> [sensor_id]")
