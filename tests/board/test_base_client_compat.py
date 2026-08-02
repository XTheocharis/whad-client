import pytest

from whad.ble.connector import BLE
from whad.device.mock import MockDevice
from whad.esb.connector import ESB
from whad.hub.discovery import Capability, DeviceType, Domain


RAW_WHAD_CAPS = {
    Domain.BtLE: (
        Capability.Sniff | Capability.Inject,
        [],
    ),
    Domain.Dot15d4: (
        Capability.Sniff | Capability.Inject | Capability.Jam,
        [],
    ),
    Domain.Esb: (
        Capability.Sniff | Capability.Inject,
        [],
    ),
    Domain.LogitechUnifying: (
        Capability.Sniff | Capability.Inject,
        [],
    ),
    Domain.Phy: (
        Capability.Sniff | Capability.NoRawData,
        [],
    ),
}

BOARD_CAPS = {
    Domain.Board: (
        Capability.Read | Capability.Write,
        [],
    ),
}


def _make_device(caps):
    return MockDevice(
        "whad-team",
        "https://whad.io",
        proto_minver=2,
        version="1.0.0",
        dev_type=DeviceType.VirtualDevice,
        dev_id=b"CompatMock",
        capabilities=caps,
    )


def test_clue_device_advertises_six_domains():
    caps = {**RAW_WHAD_CAPS, **BOARD_CAPS}
    dev = _make_device(caps)
    dev.open()
    dev.discover()
    try:
        domains = dev.get_domains()
        assert Domain.BtLE in domains
        assert Domain.Dot15d4 in domains
        assert Domain.Esb in domains
        assert Domain.LogitechUnifying in domains
        assert Domain.Phy in domains
        assert Domain.Board in domains
        assert len(domains) == 6
    finally:
        dev.close()


def test_ble_connector_works_with_board_present():
    caps = {**RAW_WHAD_CAPS, **BOARD_CAPS}
    dev = _make_device(caps)
    conn = BLE(dev)
    try:
        assert conn.domain == "ble"
        assert dev.has_domain(Domain.BtLE)
        assert dev.has_domain(Domain.Board)
    finally:
        conn.close()


def test_ble_connector_works_without_board():
    dev = _make_device(RAW_WHAD_CAPS)
    conn = BLE(dev)
    try:
        assert conn.domain == "ble"
        assert dev.has_domain(Domain.BtLE)
        assert not dev.has_domain(Domain.Board)
    finally:
        conn.close()


def test_esb_connector_works_with_board_present():
    caps = {**RAW_WHAD_CAPS, **BOARD_CAPS}
    dev = _make_device(caps)
    conn = ESB(dev)
    try:
        assert conn.domain == "esb"
        assert dev.has_domain(Domain.Esb)
        assert dev.has_domain(Domain.Board)
    finally:
        dev.close()


def test_esb_connector_works_without_board():
    dev = _make_device(RAW_WHAD_CAPS)
    conn = ESB(dev)
    try:
        assert conn.domain == "esb"
        assert not dev.has_domain(Domain.Board)
    finally:
        dev.close()


def test_non_clue_device_has_five_domains():
    dev = _make_device(RAW_WHAD_CAPS)
    dev.open()
    dev.discover()
    try:
        domains = dev.get_domains()
        assert Domain.Board not in domains
        assert len(domains) == 5
    finally:
        dev.close()


def test_board_capability_does_not_bleed_into_radio_caps():
    caps = {**RAW_WHAD_CAPS, **BOARD_CAPS}
    dev = _make_device(caps)
    dev.open()
    dev.discover()
    try:
        ble_cap = dev.get_domain_capability(Domain.BtLE)
        board_cap = dev.get_domain_capability(Domain.Board)

        assert board_cap == (Capability.Read | Capability.Write)
        assert ble_cap == (Capability.Sniff | Capability.Inject)
        assert ble_cap != board_cap
    finally:
        dev.close()


def test_board_connector_rejects_non_board_device():
    from whad.board.connector.base import BoardConnector
    from whad.exceptions import UnsupportedDomain

    dev = _make_device(RAW_WHAD_CAPS)
    with pytest.raises(UnsupportedDomain):
        BoardConnector(dev)
