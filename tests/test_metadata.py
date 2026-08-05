"""Tests for whad.hub.discovery.metadata module."""
from whad.hub.discovery import Domain, Capability
from whad.hub.discovery.metadata import (
    DOMAINS,
    CAPABILITIES,
    COMMANDS,
    list_domain_details,
    list_capability_details,
    list_command_details,
)


def test_domains_dict_matches_domain_class():
    """Drift detection: DOMAINS keys must match Domain class bitmask constants."""
    domain_values = {
        v for k, v in vars(Domain).items()
        if not k.startswith('_') and k != 'DomainNone'
    }
    assert set(DOMAINS.keys()) == domain_values, (
        f"DOMAINS dict keys drifted from Domain class. "
        f"Missing from DOMAINS: {domain_values - set(DOMAINS.keys())}, "
        f"Extra in DOMAINS: {set(DOMAINS.keys()) - domain_values}"
    )

def test_capabilities_dict_matches_capability_class():
    """Drift detection: CAPABILITIES keys must match Capability class constants."""
    cap_values = {
        v for k, v in vars(Capability).items()
        if not k.startswith('_') and k != 'CapNone'
    }
    assert set(CAPABILITIES.keys()) == cap_values

def test_domains_has_12_entries():
    assert len(DOMAINS) == 12

def test_commands_covers_all_domain_dicts():
    """COMMANDS dict must reference all 6 per-domain command dicts."""
    assert len(COMMANDS) == 6


def test_ble_commands_drift():
    """Drift detection: BLE_COMMANDS keys match BleCommands class."""
    from whad.hub.ble import Commands as BleCommands
    from whad.hub.discovery.metadata import BLE_COMMANDS
    cmd_values = {v for k, v in vars(BleCommands).items() if not k.startswith('_')}
    assert set(BLE_COMMANDS.keys()) == cmd_values, (
        f"BLE_COMMANDS drifted. Missing: {cmd_values - set(BLE_COMMANDS.keys())}, "
        f"Extra: {set(BLE_COMMANDS.keys()) - cmd_values}"
    )


def test_dot15d4_commands_drift():
    """Drift detection: DOT15D4_COMMANDS keys match Dot15d4Commands class."""
    from whad.hub.dot15d4 import Commands as Dot15d4Commands
    from whad.hub.discovery.metadata import DOT15D4_COMMANDS
    cmd_values = {v for k, v in vars(Dot15d4Commands).items() if not k.startswith('_')}
    assert set(DOT15D4_COMMANDS.keys()) == cmd_values


def test_esb_commands_drift():
    """Drift detection: ESB_COMMANDS keys match ESBCommands class."""
    from whad.hub.esb import Commands as ESBCommands
    from whad.hub.discovery.metadata import ESB_COMMANDS
    cmd_values = {v for k, v in vars(ESBCommands).items() if not k.startswith('_')}
    assert set(ESB_COMMANDS.keys()) == cmd_values


def test_unifying_commands_drift():
    """Drift detection: UNIFYING_COMMANDS keys match UnifyingCommands class."""
    from whad.hub.unifying import Commands as UnifyingCommands
    from whad.hub.discovery.metadata import UNIFYING_COMMANDS
    cmd_values = {v for k, v in vars(UnifyingCommands).items() if not k.startswith('_')}
    assert set(UNIFYING_COMMANDS.keys()) == cmd_values


def test_phy_commands_drift():
    """Drift detection: PHY_COMMANDS keys match PhyCommands class."""
    from whad.hub.phy import Commands as PhyCommands
    from whad.hub.discovery.metadata import PHY_COMMANDS
    cmd_values = {v for k, v in vars(PhyCommands).items() if not k.startswith('_')}
    assert set(PHY_COMMANDS.keys()) == cmd_values


def test_board_commands_drift():
    """Drift detection: BOARD_COMMANDS keys match BoardCommands class."""
    from whad.hub.board import Commands as BoardCommands
    from whad.hub.discovery.metadata import BOARD_COMMANDS
    cmd_values = {v for k, v in vars(BoardCommands).items() if not k.startswith('_')}
    assert set(BOARD_COMMANDS.keys()) == cmd_values


def test_all_constants_have_docstrings():
    """Every Domain, Capability, and Commands constant must resolve to a non-empty
    description via ``list_domain_details``/``list_capability_details``/
    ``list_command_details``.

    Sphinx ``#:`` comments on plain int constants don't propagate to runtime
    ``__doc__``, so the introspection functions fall back to the hand-maintained
    metadata dicts. This test catches both missing ``#:`` comments and missing
    dict entries (either path provides the description).
    """
    domain_details = list_domain_details()
    for name, value in vars(Domain).items():
        if name.startswith('_') or name == 'DomainNone':
            continue
        assert value in domain_details, f"Domain.{name} missing from list_domain_details"
        assert domain_details[value], f"Domain.{name} has no docstring"

    cap_details = list_capability_details()
    for name, value in vars(Capability).items():
        if name.startswith('_') or name == 'CapNone':
            continue
        assert value in cap_details, f"Capability.{name} missing from list_capability_details"
        assert cap_details[value], f"Capability.{name} has no docstring"

    cmd_details = list_command_details()
    for domain_value, cmd_dict in COMMANDS.items():
        assert domain_value in cmd_details, f"Domain {domain_value} missing from list_command_details"
        for cmd_value, cmd_desc in cmd_dict.items():
            assert cmd_value in cmd_details[domain_value], (
                f"command {cmd_value} missing from list_command_details for domain {domain_value}"
            )
            assert cmd_details[domain_value][cmd_value], (
                f"command {cmd_value} for domain {domain_value} has no docstring"
            )
