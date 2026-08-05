from whad.device import Device
from whad.board.connector.base import BoardConnector
import sys

if len(sys.argv) >= 2:
    interface = sys.argv[1]
    # Create the Board connector & the WHAD device
    connector = BoardConnector(Device.create(interface))

    # Query board info
    info = connector.get_board_info()
    print("[i] Board name: ", info.board_name)
    print("[i] Firmware version: ", info.firmware_version)
    print("[i] Hardware: ", info.hardware_revision)
    print("[i] Sensor count: ", info.implemented_sensor_count)
    print("[i] Active runtime: ", info.active_runtime)

    connector.close()
else:
    print("Usage: ", sys.argv[0]+" <interface>")
