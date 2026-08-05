from whad.device import Device
from whad.board.connector.base import BoardConnector
import sys

if len(sys.argv) >= 2:
    interface = sys.argv[1]
    # Create the Board connector & the WHAD device
    connector = BoardConnector(Device.create(interface))

    # BoardConnector has no get_runtime_config() wrapper; use the raw hub message.
    msg = connector.hub.board.create_get_runtime_config(request_id=0)
    resp = connector.send_request(msg, timeout=2.0)
    print("[i] Active runtime: ", resp.active_runtime)
    print("[i] BLE pairable: ", resp.ble_pairable)
    print("[i] BLE connected: ", resp.ble_connected)
    print("[i] Bond count: ", resp.bond_count)
    print("[i] Persistence available: ", resp.persistence_available)

    connector.close()
else:
    print("Usage: ", sys.argv[0]+" <interface>")
