"""Interactive shell for the wboard CLI.

Holds a single BoardConnector open across multiple commands, eliminating
the ~4s CDC re-enumeration delay between separate CLI invocations.

    wboard -i uart0 shell
"""
from prompt_toolkit import HTML

from whad.cli.shell import InteractiveShell, category

RUNTIME_NAMES = {
    0: "UNKNOWN",
    1: "RAW_WHAD",
    2: "BLE_HID",
}


def _runtime_label(value):
    return RUNTIME_NAMES.get(value, str(value))


class BoardShell(InteractiveShell):
    """Interactive shell wrapping a BoardConnector."""

    def __init__(self, connector, timeout=2.0):
        super().__init__(HTML("<b>wboard></b> "))
        self._connector = connector
        self._timeout = timeout

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _send(self, message):
        return self._connector.send_request(message, timeout=self._timeout)

    # ------------------------------------------------------------------
    # commands
    # ------------------------------------------------------------------
    @category("Board")
    def do_info(self, _):
        """show board information

        <ansicyan><b>info</b></ansicyan>

        Display board name, hardware/firmware revisions, active runtime,
        and implemented sensor count.
        """
        response = self._connector.get_board_info(timeout=self._timeout)
        if response is None:
            self.error("No response from device.")
            return
        print(f"  board name      : {response.board_name}")
        print(f"  hardware        : {response.hardware_revision}")
        print(f"  firmware        : {response.firmware_version}")
        print(f"  protocol variant: {response.protocol_variant}")
        print(f"  active runtime  : {_runtime_label(response.active_runtime)}")
        print(f"  sensors         : {response.implemented_sensor_count}")

    @category("Sensors")
    def do_sensors(self, _):
        """list available sensors

        <ansicyan><b>sensors</b></ansicyan>

        Paginate through sensor descriptors and print a table.
        """
        cursor = 0
        print(f"  {'ID':>3}  {'Name':<18} {'Unit':<14} {'Values':>6}")
        print(f"  {'---':>3}  {'----':<18} {'----':<14} {'------':>6}")
        while True:
            response = self._connector.list_sensors(
                cursor=cursor, timeout=self._timeout)
            if response is None:
                self.error("No response from device.")
                return
            descriptor = response.descriptor
            if response.message.board.sensor_descriptor.HasField("descriptor"):
                name = descriptor.name
                unit = descriptor.unit
                value_count = descriptor.value_count
            else:
                name = "?"
                unit = "?"
                value_count = 0
            print(f"  {descriptor.sensor_id:>3}  {name:<18} {unit:<14} {value_count:>6}")
            if response.eof or response.next_cursor == 0:
                break
            cursor = response.next_cursor

    @category("Sensors")
    def do_sensor_read(self, args):
        """read a single sample from a sensor

        <ansicyan><b>sensor_read</b> <i>SENSOR_ID</i></ansicyan>

        Read one sample from the given sensor and display its values.
        """
        if len(args) < 1:
            self.error("sensor_read requires a sensor ID.")
            return
        try:
            sensor_id = int(args[0], 0)
        except ValueError:
            self.error(f"Invalid sensor ID: {args[0]}")
            return
        response = self._connector.read_sensor(sensor_id, timeout=self._timeout)
        if response is None:
            self.error("No response from device.")
            return
        values = list(response.values) if response.values else []
        print(f"  sensor_id={response.sensor_id} sequence={response.sequence} "
              f"status={response.status:#x} values={values}")

    @category("Expert I/O")
    def do_gpio_read(self, args):
        """read a GPIO pin

        <ansicyan><b>gpio_read</b> <i>PIN</i></ansicyan>

        Read the logical level of the given GPIO pin.
        """
        if len(args) < 1:
            self.error("gpio_read requires a pin number.")
            return
        try:
            pin = int(args[0], 0)
        except ValueError:
            self.error(f"Invalid pin: {args[0]}")
            return
        message = self._connector.hub.board.create_gpio_read(pin=pin)
        response = self._send(message)
        if response is None:
            self.error("No response from device.")
            return
        print(f"  pin={response.pin} value={bool(response.value)} "
              f"result={response.result}")

    @category("Expert I/O")
    def do_gpio_write(self, args):
        """write a GPIO pin

        <ansicyan><b>gpio_write</b> <i>PIN</i> <i>VALUE</i></ansicyan>

        Drive the given GPIO pin to 0 (low) or 1 (high).
        """
        if len(args) < 2:
            self.error("gpio_write requires a pin and a value (0 or 1).")
            return
        try:
            pin = int(args[0], 0)
            value = int(args[1], 0)
        except ValueError:
            self.error(f"Invalid arguments: {args}")
            return
        message = self._connector.hub.board.create_gpio_write(
            pin=pin, value=value)
        response = self._send(message)
        if response is None:
            self.error("No response from device.")
            return
        print(f"  result={response.result}")

    @category("Runtime")
    def do_runtime_config(self, _):
        """show runtime configuration

        <ansicyan><b>runtime_config</b></ansicyan>

        Display the active runtime mode, persisted mode, BLE status, and
        persistence availability.
        """
        message = self._connector.hub.board.create_get_runtime_config()
        response = self._send(message)
        if response is None:
            self.error("No response from device.")
            return
        print(f"  active runtime      : {_runtime_label(response.active_runtime)}")
        print(f"  persisted runtime   : {_runtime_label(response.persisted_runtime)}")
        print(f"  persistence avail.  : {response.persistence_available}")
        print(f"  BLE advertising     : {response.ble_advertising}")
        print(f"  BLE pairable        : {response.ble_pairable}")
        print(f"  BLE connected       : {response.ble_connected}")
        print(f"  bond count          : {response.bond_count}")

    @category("Storage")
    def do_storage_info(self, _):
        """show QSPI storage information

        <ansicyan><b>storage_info</b></ansicyan>

        Display the storage adoption state, capacity, used bytes, log
        record count, erase size, and JEDEC ID.
        """
        response = self._connector.storage_info(timeout=self._timeout)
        if response is None:
            self.error("No response from device.")
            return
        jedec = response.jedec_id.hex() if response.jedec_id else ""
        print(f"  state        : {response.state}")
        print(f"  capacity     : {response.capacity_bytes} bytes")
        print(f"  used         : {response.used_bytes} bytes")
        print(f"  log records  : {response.log_records}")
        print(f"  erase size   : {response.erase_size} bytes")
        print(f"  JEDEC ID     : {jedec}")

    @category("Storage")
    def do_storage_adopt(self, args):
        """adopt the QSPI storage (erases flash!)

        <ansicyan><b>storage_adopt</b> <i>CONFIRM_NONCE</i></ansicyan>

        Adopt the QSPI storage. This ERASES the flash and writes a fresh
        journal header. Requires an explicit confirm nonce to proceed.
        """
        if len(args) < 1:
            self.error("storage_adopt requires a confirm nonce.")
            return
        try:
            confirm_nonce = int(args[0], 0)
        except ValueError:
            self.error(f"Invalid nonce: {args[0]}")
            return
        confirmed = input(
            "This will ERASE the flash. Type 'yes' to confirm: ").strip()
        if confirmed.lower() != "yes":
            print("Aborted.")
            return
        response = self._connector.storage_adopt(
            confirm_nonce=confirm_nonce, timeout=self._timeout)
        if response is None:
            self.error("No response from device.")
            return
        print(f"  state={response.state} result=ok")

    # ------------------------------------------------------------------
    # quit: break the loop but do NOT close the connector
    # (wboard.py's run() finally block owns cleanup).
    # ------------------------------------------------------------------
    def do_quit(self, _):
        """exit the shell

        <ansicyan><b>quit</b></ansicyan>

        Leave the interactive shell. The BoardConnector is closed by
        wboard after the shell exits.
        """
        return True

    def do_exit(self, args):
        """alias for <ansicyan>quit</ansicyan>

        <ansicyan><b>exit</b></ansicyan>
        """
        return self.do_quit(args)
