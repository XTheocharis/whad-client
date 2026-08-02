"""Storage and calibration persistence integration tests (Todo 30)."""
import pytest

from whad.board.connector.base import BoardConnector
from whad.device.mock import MockDevice
from whad.hub.board import (
    BoardCommandResult,
    Commands,
    LogChunk,
    StorageAdoptRequest,
    StorageEraseLogRequest,
    StorageInfoRequest,
    StorageInfoResponse,
)
from whad.hub.discovery import Capability, DeviceType, Domain
from whad.protocol.board import board_pb2 as pb


STORAGE_COMMANDS = [
    Commands.GetBoardInfo,
    Commands.GetRuntimeConfig,
    Commands.SetRuntimeConfig,
    Commands.SetRuntimeMode,
    Commands.StorageInfo,
    Commands.StorageAdopt,
    Commands.StorageReadLog,
    Commands.StorageEraseLog,
]


class StorageMockDevice(MockDevice):
    """Mock device emulating storage adoption, log reads, and erase."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._adopted = False
        self._log_records = []

    @MockDevice.route(StorageInfoRequest)
    def on_storage_info(self, message):
        state = (
            pb.StorageState.STORAGE_ADOPTED if self._adopted
            else pb.StorageState.STORAGE_UNADOPTED
        )
        return self.hub.board.create(
            "storage_status",
            request_id=message.request_id,
            state=state,
            capacity_bytes=0x200000 if self._adopted else 0,
            used_bytes=0,
            log_records=len(self._log_records),
            erase_size=4096,
            jedec_id=b"\xC8\x40\x15",
        )

    @MockDevice.route(StorageAdoptRequest)
    def on_storage_adopt(self, message):
        if self._adopted:
            return self.hub.board.create_command_result(
                request_id=message.request_id,
                command=pb.BoardCommand.StorageAdopt,
                result=pb.BoardResultCode.WRONG_MODE,
                terminal=True,
                detail=b"already adopted",
            )
        if message.confirm_nonce == 0:
            return self.hub.board.create_command_result(
                request_id=message.request_id,
                command=pb.BoardCommand.StorageAdopt,
                result=pb.BoardResultCode.PERMISSION_DENIED,
                terminal=True,
                detail=b"nonce required",
            )
        self._adopted = True
        return self.hub.board.create_command_result(
            request_id=message.request_id,
            command=pb.BoardCommand.StorageAdopt,
            result=pb.BoardResultCode.SUCCESS,
            terminal=True,
            detail=b"adopted",
        )

    @MockDevice.route(StorageEraseLogRequest)
    def on_storage_erase_log(self, message):
        if not self._adopted:
            return self.hub.board.create_command_result(
                request_id=message.request_id,
                command=pb.BoardCommand.StorageEraseLog,
                result=pb.BoardResultCode.NOT_ADOPTED,
                terminal=True,
                detail=b"",
            )
        if message.confirm_nonce == 0:
            return self.hub.board.create_command_result(
                request_id=message.request_id,
                command=pb.BoardCommand.StorageEraseLog,
                result=pb.BoardResultCode.PERMISSION_DENIED,
                terminal=True,
                detail=b"nonce required",
            )
        self._log_records.clear()
        return self.hub.board.create_command_result(
            request_id=message.request_id,
            command=pb.BoardCommand.StorageEraseLog,
            result=pb.BoardResultCode.SUCCESS,
            terminal=True,
            detail=b"erased",
        )


@pytest.fixture
def storage_device():
    capabilities = {
        Domain.Board: (
            Capability.Read | Capability.Write | Capability.Store,
            STORAGE_COMMANDS,
        )
    }
    return StorageMockDevice(
        author="whad-team",
        url="https://whad.io",
        proto_minver=2,
        version="1.0.0",
        dev_type=DeviceType.VirtualDevice,
        dev_id=b"StorageMock",
        capabilities=capabilities,
    )


@pytest.fixture
def connector(storage_device):
    conn = BoardConnector(storage_device)
    yield conn
    conn.close()


def test_storage_info_unadopted(connector):
    response = connector.storage_info(timeout=2.0)
    assert isinstance(response, StorageInfoResponse)
    assert response.state == pb.StorageState.STORAGE_UNADOPTED
    assert response.jedec_id == b"\xC8\x40\x15"


def test_storage_adopt_without_nonce_permission_denied(connector):
    response = connector.storage_adopt(confirm_nonce=0, timeout=2.0)
    assert isinstance(response, BoardCommandResult)
    assert response.result == pb.BoardResultCode.PERMISSION_DENIED
    assert response.terminal is True


def test_storage_adopt_with_nonce_succeeds(connector):
    response = connector.storage_adopt(confirm_nonce=12345, timeout=2.0)
    assert isinstance(response, BoardCommandResult)
    assert response.result == pb.BoardResultCode.SUCCESS
    assert response.terminal is True


def test_storage_adopt_double_adopt_wrong_mode(connector):
    connector.storage_adopt(confirm_nonce=12345, timeout=2.0)
    response = connector.storage_adopt(confirm_nonce=99999, timeout=2.0)
    assert isinstance(response, BoardCommandResult)
    assert response.result == pb.BoardResultCode.WRONG_MODE


def test_storage_info_after_adoption(connector):
    connector.storage_adopt(confirm_nonce=12345, timeout=2.0)
    response = connector.storage_info(timeout=2.0)
    assert isinstance(response, StorageInfoResponse)
    assert response.state == pb.StorageState.STORAGE_ADOPTED
    assert response.capacity_bytes == 0x200000


def test_storage_erase_log_without_adoption_rejected(connector):
    response = connector.storage_erase_log(confirm_nonce=1, timeout=2.0)
    assert isinstance(response, BoardCommandResult)
    assert response.result == pb.BoardResultCode.NOT_ADOPTED


def test_storage_erase_log_without_nonce_denied(connector):
    connector.storage_adopt(confirm_nonce=12345, timeout=2.0)
    response = connector.storage_erase_log(confirm_nonce=0, timeout=2.0)
    assert isinstance(response, BoardCommandResult)
    assert response.result == pb.BoardResultCode.PERMISSION_DENIED


def test_storage_erase_log_after_adoption_succeeds(connector):
    connector.storage_adopt(confirm_nonce=12345, timeout=2.0)
    connector.device._log_records = list(range(100))
    response = connector.storage_erase_log(confirm_nonce=1, timeout=2.0)
    assert isinstance(response, BoardCommandResult)
    assert response.result == pb.BoardResultCode.SUCCESS
    assert len(connector.device._log_records) == 0


def test_storage_command_bits_advertised(storage_device):
    storage_device.discover()
    commands = storage_device.get_domain_commands(Domain.Board)
    assert (commands & (1 << Commands.StorageInfo)) != 0
    assert (commands & (1 << Commands.StorageAdopt)) != 0
    assert (commands & (1 << Commands.StorageReadLog)) != 0
    assert (commands & (1 << Commands.StorageEraseLog)) != 0


def test_non_adopted_calibration_is_volatile(storage_device, connector):
    storage_device.discover()
    commands = storage_device.get_domain_commands(Domain.Board)
    assert (commands & (1 << Commands.StorageAdopt)) != 0
    response = connector.storage_info(timeout=2.0)
    assert response.state == pb.StorageState.STORAGE_UNADOPTED


def test_storage_adopt_then_info_state_changes(connector):
    info1 = connector.storage_info(timeout=2.0)
    assert info1.state == pb.StorageState.STORAGE_UNADOPTED
    connector.storage_adopt(confirm_nonce=42, timeout=2.0)
    info2 = connector.storage_info(timeout=2.0)
    assert info2.state == pb.StorageState.STORAGE_ADOPTED
