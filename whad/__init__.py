"""
WHAD - Wireless HAcking Devices

This is the main WHAD client module.
"""
import logging

# CDC ACM termios compatibility shim.
# Must be imported before pyserial is used at runtime: some kernel cdc_acm
# drivers (e.g. Linux 7.1.5 for the WHAD ButteRFly dongle) return ENOTTY for
# tcgetattr/tcsetattr/tcflush, which makes pyserial's Serial() fail at open
# time. The shim patches termios to swallow those errors for affected devices.
from whad import _termios_patch  # noqa: F401

from whad.device import WhadDevice
from whad.exceptions import RequiredImplementation, UnsupportedDomain, \
    UnsupportedCapability, WhadDeviceNotReady, WhadDeviceNotFound, \
    WhadDeviceAccessDenied

# Force scapy to hide warnings
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)


__all__ = [
    'UartDevice',
    'VirtualDevice',
    'WhadDevice',
    'RequiredImplementation',
    'UnsupportedDomain',
    'UnsupportedCapability',
    'WhadDeviceNotReady',
    'WhadDeviceNotFound',
    'WhadDeviceAccessDenied'
]
