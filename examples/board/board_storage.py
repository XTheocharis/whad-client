from whad.device import Device
from whad.board.connector.base import BoardConnector
import sys

if len(sys.argv) >= 2:
    interface = sys.argv[1]
    # Create the Board connector & the WHAD device
    connector = BoardConnector(Device.create(interface))

    # Query QSPI storage info
    storage = connector.storage_info()
    print("[i] Adoption state: ", storage.state)
    print("[i] Capacity (bytes): ", storage.capacity_bytes)
    print("[i] Used (bytes): ", storage.used_bytes)
    print("[i] Log record count: ", storage.log_records)

    connector.close()
else:
    print("Usage: ", sys.argv[0]+" <interface>")
