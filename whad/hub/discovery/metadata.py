"""Hardcoded display metadata for WHAD domains, capabilities, and commands.

These dicts map generated bitmask constants (``Domain``, ``Capability``, and
per-domain ``Commands`` enums) to the human-readable strings shown by the
``whadup`` CLI. The prose descriptions have no introspectable source — they are
hand-maintained here so that any new domain/capability/command MUST be added
explicitly rather than discovered at runtime.

A drift-detection test (``tests/test_metadata.py``) asserts that ``DOMAINS`` and
``CAPABILITIES`` stay in sync with their respective classes in
``whad.hub.discovery``.
"""
from whad.hub.discovery import Domain, Capability
from whad.hub.ble import Commands as BleCommands
from whad.hub.dot15d4 import Commands as Dot15d4Commands
from whad.hub.esb import Commands as ESBCommands
from whad.hub.unifying import Commands as UnifyingCommands
from whad.hub.phy import Commands as PhyCommands
from whad.hub.board import Commands as BoardCommands


DOMAINS = {
    Domain.Phy: "Physical Layer",
    Domain.ANT: "ANT",
    Domain.ANT_FS: "ANT FS",
    Domain.ANT_Plus: "ANT+",
    Domain.BtClassic: "Bluetooth Classic",
    Domain.BtLE: "Bluetooth LE",
    Domain.Esb: "Enhanced ShockBurst",
    Domain.LogitechUnifying: "Logitech Unifying",
    Domain.Mosart: "Mosart",
    Domain.SixLowPan: "6LowPan",
    Domain.Dot15d4: "802.15.4",
    Domain.Board: "Board"
}

CAPABILITIES = {
    Capability.Scan: "can scan devices",
    Capability.Hijack: "can hijack communication",
    Capability.Hook: "can hook packets",
    Capability.Inject: "can inject packets",
    Capability.Jam: "can jam communications",
    Capability.SimulateRole: "can simulate a role in a communication",
    Capability.Sniff: "can sniff data",
    Capability.NoRawData: "can not read/write raw packet",
    Capability.Read: "can read board resources",
    Capability.Write: "can write board resources",
    Capability.Stream: "can stream board events",
    Capability.Store: "can use board storage"
}

BLE_COMMANDS = {
    BleCommands.SetBdAddress: "SetBdAddress: can set BD address",
    BleCommands.SniffAdv: "SniffAdv: can sniff advertising PDUs",
    BleCommands.JamAdv: "JamAdv: can jam advertising PDUs",
    BleCommands.JamAdvOnChannel: "JamAdvOnChannel: can jam advertising PDUs on a single channel",
    BleCommands.ReactiveJam: "ReactiveJam: can reactively jam PDU on a single channel",
    BleCommands.SniffConnReq: "SniffConnReq: can sniff a new connection",
    BleCommands.SniffAccessAddress: "SniffAccessAddress: can detect active connections",
    BleCommands.SniffActiveConn: "SniffActiveConn: can sniff an active connection",
    BleCommands.JamConn: "JamConn: can jam an active connection",
    BleCommands.ScanMode: "ScanMode: can scan devices",
    BleCommands.AdvMode: "AdvMode: can advertise as a BLE device",
    BleCommands.SetAdvData: "SetAdvData: can set advertising PDU details",
    BleCommands.CentralMode: "CentralMode: can act as a Central device",
    BleCommands.ConnectTo: "ConnectTo: can initiate a BLE connection",
    BleCommands.SendRawPDU: "SendRawPDU: can send a raw PDU",
    BleCommands.SendPDU: "SendPDU: can send a PDU",
    BleCommands.Disconnect: "Disconnect: can terminate an active connection (in Central mode)",
    BleCommands.PeripheralMode: "PeripheralMode: can act as a peripheral",
    BleCommands.Start: "Start: can start depending on the current mode",
    BleCommands.Stop: "Stop: can stop depending on the current mode",
    BleCommands.SetEncryption: "SetEncryption: can enable encryption during a connection",
    BleCommands.HijackMaster: "HijackMaster: can hijack the Master role in an active connection",
    BleCommands.HijackSlave: "HijackSlave: can hijack the Slave role in an active connection",
    BleCommands.HijackBoth: (
        "HijackBoth: can hijack the Master and the Slave role in an active connection"
    ),
    BleCommands.PrepareSequence: (
        "PrepareSequence: can prepare a sequence of packets and associate a trigger"
    ),
    BleCommands.TriggerSequence: (
        "TriggerSequence: can manually trigger the transmission of a sequence of packets"
    ),
    BleCommands.DeleteSequence: "DeleteSequence: can delete a prepared sequence of packets"

}

DOT15D4_COMMANDS = {
    Dot15d4Commands.SetNodeAddress: "SetNodeAddress: can set Node address",
    Dot15d4Commands.Sniff: "Sniff: can sniff 802.15.4 packets",
    Dot15d4Commands.EnergyDetection: "EnergyDetection: can perform energy detection scans",
    Dot15d4Commands.Jam: "Jam: can jam 802.15.4 packets",
    Dot15d4Commands.Send: "Send: can transmit 802.15.4 packets",
    Dot15d4Commands.SendRaw: "SendRaw: can transmit raw 802.15.4 packets",
    Dot15d4Commands.EndDeviceMode: "EndDeviceMode: can act as an End Device",
    Dot15d4Commands.CoordinatorMode: "CoordinatorMode: can act as a Coordinator",
    Dot15d4Commands.RouterMode: "RouterMode: can act as a Router",
    Dot15d4Commands.Start: "Start: can start depending on the current mode",
    Dot15d4Commands.Stop: "Stop: can stop depending on the current mode",
    Dot15d4Commands.ManInTheMiddle: "ManInTheMiddle: can perform a Man-in-the-Middle attack",
}

ESB_COMMANDS = {
    ESBCommands.SetNodeAddress: "SetNodeAddress: can set Node address",
    ESBCommands.Sniff: "Sniff: can sniff Enhanced ShockBurst packets",
    ESBCommands.Jam: "Jam: can jam Enhanced ShockBurst packets",
    ESBCommands.Send: "Send: can transmit Enhanced ShockBurst packets",
    ESBCommands.SendRaw: "SendRaw: can transmit raw Enhanced ShockBurst packets",
    ESBCommands.PrimaryReceiverMode: "PrimaryReceiverMode: can act as a Primary Receiver (PRX)",
    ESBCommands.PrimaryTransmitterMode: "PrimaryTransmitterMode: can act as a Primary Transmitter (PTX)",
    ESBCommands.Start: "Start: can start depending on the current mode",
    ESBCommands.Stop: "Stop: can stop depending on the current mode"
}

UNIFYING_COMMANDS = {
    UnifyingCommands.SetNodeAddress: "SetNodeAddress: can set Node address",
    UnifyingCommands.Sniff: "Sniff: can sniff Logitech Unifying packets",
    UnifyingCommands.Jam: "Jam: can jam Logitech Unifying packets",
    UnifyingCommands.Send: "Send: can transmit Logitech Unifying packets",
    UnifyingCommands.SendRaw: "SendRaw: can transmit raw Logitech Unifying packets",
    UnifyingCommands.LogitechDongleMode: (
        "PrimaryReceiverMode: can act as a Logitech Dongle (ESB PRX)"
    ),
    UnifyingCommands.LogitechKeyboardMode: (
        "PrimaryReceiverMode: can act as a Logitech Keyboard (ESB PTX)"
    ),
    UnifyingCommands.LogitechMouseMode: (
        "LogitechMouseMode: can act as a Logitech Mouse (ESB PTX)"
    ),
    UnifyingCommands.Start: "Start: can start depending on the current mode",
    UnifyingCommands.Stop: "Stop: can stop depending on the current mode",
    UnifyingCommands.SniffPairing: "SniffPairing: can sniff a pairing process"
}

PHY_COMMANDS = {
    PhyCommands.SetASKModulation: (
        "SetASKModulation: can use Amplitude Shift Keying modulation scheme"
    ),
    PhyCommands.SetFSKModulation: (
        "SetFSKModulation: can use Frequency Shift Keying modulation scheme"
    ),
    PhyCommands.SetGFSKModulation: (
        "SetGFSKModulation: can use Gaussian Frequency Shift Keying modulation scheme"
    ),
    PhyCommands.SetBPSKModulation: (
        "SetBPSKModulation: can use Binary Phase Shift Keying modulation scheme"
    ),
    PhyCommands.SetQPSKModulation: (
        "SetQPSKModulation: can use Quadrature Phase Shift Keying modulation scheme"
    ),
    PhyCommands.SetLoRaModulation: (
        "SetLoRaModulation: can use LoRa modulation scheme"
    ),
    PhyCommands.Set4FSKModulation: (
        "Set4FSKModulation: can use 4-FSK modulation scheme"
    ),
    PhyCommands.SetMSKModulation: (
        "SetMSKModulation: can use Minimum Shift Keying modulation scheme"
    ),
    PhyCommands.GetSupportedFrequencies: (
        "GetSupportedFrequencies: can return a list of supported frequency ranges"
    ),
    PhyCommands.SetFrequency: "SetFrequency: can configure a given frequency",
    PhyCommands.SetDataRate: "SetDataRate: can configure the datarate",
    PhyCommands.SetEndianness: "SetEndianness: can configure the endianness",
    PhyCommands.SetTXPower: "SetTXPower: can configure the transmission power level",
    PhyCommands.SetPacketSize: "SetPacketSize: can configure the packet size",
    PhyCommands.SetSyncWord: "SetSyncWord: can configure the synchronization word",
    PhyCommands.Sniff: "Sniff: can receive arbitrary packets",
    PhyCommands.Send: "Send: can transmit arbitrary packets",
    PhyCommands.SendRaw: "SendRaw: can transmit arbitrary IQ streams" ,
    PhyCommands.ScheduleSend: "ScheduleSend: can schedule a packet to be sent at a specific time",
    PhyCommands.Jam: "Jam: can jam a physical medium",
    PhyCommands.Monitor: "Monitor: can monitor a physical medium",
    PhyCommands.Start: "Start: can start depending on the current mode",
    PhyCommands.Stop: "Stop: can stop depending on the current mode",
}

BOARD_COMMANDS = {
    BoardCommands.GetBoardInfo: "GetBoardInfo: can read board information",
    BoardCommands.ListSensors: "ListSensors: can enumerate board sensors",
    BoardCommands.ReadSensor: "ReadSensor: can read one sensor sample",
    BoardCommands.ConfigureStream: "ConfigureStream: can configure sensor streams",
    BoardCommands.StopStream: "StopStream: can stop sensor streams",
    BoardCommands.Calibrate: "Calibrate: can calibrate sensors",
    BoardCommands.GetCalibration: "GetCalibration: can read calibration data",
    BoardCommands.SetOutput: "SetOutput: can control outputs",
    BoardCommands.GetInputState: "GetInputState: can read input state",
    BoardCommands.ConfigureInput: "ConfigureInput: can configure input behavior",
    BoardCommands.I2cTransfer: "I2cTransfer: can run I2C transfers",
    BoardCommands.GpioConfigure: "GpioConfigure: can configure GPIO pins",
    BoardCommands.GpioRead: "GpioRead: can read GPIO pins",
    BoardCommands.GpioWrite: "GpioWrite: can write GPIO pins",
    BoardCommands.AdcRead: "AdcRead: can read ADC channels",
    BoardCommands.SpiTransfer: "SpiTransfer: can run SPI transfers",
    BoardCommands.StorageInfo: "StorageInfo: can read storage status",
    BoardCommands.StorageAdopt: "StorageAdopt: can adopt board storage",
    BoardCommands.StorageReadLog: "StorageReadLog: can read board logs",
    BoardCommands.StorageEraseLog: "StorageEraseLog: can erase board logs",
    BoardCommands.GetRuntimeConfig: "GetRuntimeConfig: can read runtime configuration",
    BoardCommands.SetRuntimeConfig: "SetRuntimeConfig: can update runtime configuration",
    BoardCommands.SetRuntimeMode: "SetRuntimeMode: can switch runtime mode",
    BoardCommands.RemoteProfileGet: "RemoteProfileGet: can read HID remote profiles",
    BoardCommands.RemoteProfileSet: "RemoteProfileSet: can write HID remote profiles",
    BoardCommands.AudioConfigure: "AudioConfigure: can configure audio metrics",
    BoardCommands.ReleasePin: "ReleasePin: can release leased resources",
    BoardCommands.RawPcmDiagnostics: "RawPcmDiagnostics: can stream raw PCM diagnostics"
}

COMMANDS = {
    Domain.BtLE: BLE_COMMANDS,
    Domain.Esb: ESB_COMMANDS,
    Domain.Dot15d4: DOT15D4_COMMANDS,
    Domain.LogitechUnifying: UNIFYING_COMMANDS,
    Domain.Phy: PHY_COMMANDS,
    Domain.Board: BOARD_COMMANDS

}


_SENTINEL_DOCSTRINGS = {
    int.__doc__,
    type(None).__doc__,
}


def _attr_doc(value):
    """Return a non-sentinel ``__doc__`` for *value*, else ``None``.

    Plain int constants share ``int.__doc__`` (class-level), which is not an
    attribute-specific docstring. We treat it (and ``None.__doc__``) as
    "no docstring" so the caller falls back to the hand-maintained dict.
    """
    doc = getattr(value, "__doc__", None)
    if not doc or doc in _SENTINEL_DOCSTRINGS:
        return None
    return doc


def list_domain_details():
    """Map every ``Domain`` constant to its human-readable description.

    Iterates ``Domain`` class attributes (skipping dunders and ``DomainNone``),
    reads ``__doc__`` when Sphinx ``#:`` comments propagated one at runtime,
    and falls back to the hand-maintained ``DOMAINS`` dict otherwise.
    """
    details = {}
    for name, value in vars(Domain).items():
        if name.startswith("_") or name == "DomainNone":
            continue
        doc = _attr_doc(value) or DOMAINS.get(value)
        details[value] = doc
    return details


def list_capability_details():
    """Map every ``Capability`` constant to its human-readable description."""
    details = {}
    for name, value in vars(Capability).items():
        if name.startswith("_") or name == "CapNone":
            continue
        doc = _attr_doc(value) or CAPABILITIES.get(value)
        details[value] = doc
    return details


def list_command_details():
    """Map every per-domain ``Commands`` constant to its human-readable description.

    Returns a dict keyed by ``Domain`` value, with each value being a
    ``{command_value: description}`` dict sourced from ``__doc__`` or the
    hand-maintained ``COMMANDS`` nested dict.
    """
    details = {}
    for domain_value, cmd_dict in COMMANDS.items():
        commands_cls = _COMMANDS_CLASSES.get(domain_value)
        if commands_cls is None:
            details[domain_value] = dict(cmd_dict)
            continue
        domain_details = {}
        for name, value in vars(commands_cls).items():
            if name.startswith("_"):
                continue
            doc = _attr_doc(value) or cmd_dict.get(value)
            domain_details[value] = doc
        details[domain_value] = domain_details
    return details


_COMMANDS_CLASSES = {
    Domain.BtLE: BleCommands,
    Domain.Esb: ESBCommands,
    Domain.Dot15d4: Dot15d4Commands,
    Domain.LogitechUnifying: UnifyingCommands,
    Domain.Phy: PhyCommands,
    Domain.Board: BoardCommands,
}
