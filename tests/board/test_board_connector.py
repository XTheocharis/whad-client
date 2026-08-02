import pytest

from whad.board.connector.base import BoardConnector
from whad.device.mock import MockDevice
from whad.hub.board import GetBoardInfoRequest, SensorSample
from whad.hub.discovery import Capability, DeviceType, Domain


class BoardMockDevice(MockDevice):
    @MockDevice.route(GetBoardInfoRequest)
    def on_get_board_info(self, message):
        event = self.hub.board.create_sensor_sample(
            request_id=0,
            sensor_id=1,
            sequence=1,
            timestamp_us=123,
            status=0,
            values=[1, 2, 3],
        )
        response = self.hub.board.create_board_info_response(
            request_id=message.request_id,
            board_name="Adafruit CLUE",
            hardware_revision="rev-a",
            firmware_version="0.1.0",
            protocol_variant="board-v1",
            device_id=b"CLUE",
            active_runtime=1,
            implemented_sensor_count=14,
        )
        return [event, response]


@pytest.fixture
def board_device():
    capabilities = {
        Domain.Board: (
            Capability.Read | Capability.Write | Capability.Stream | Capability.Store,
            [0],
        )
    }
    return BoardMockDevice(
        "whad-team",
        "https://whad.io",
        proto_minver=2,
        version="1.2.17",
        dev_type=DeviceType.VirtualDevice,
        dev_id=b"BoardMock",
        capabilities=capabilities,
    )


def test_connector_checks_board_domain_and_sets_domain_attribute(board_device):
    connector = BoardConnector(board_device)

    try:
        assert connector.domain == "board"
        assert connector.device.has_domain(Domain.Board)
    finally:
        connector.close()


def test_get_board_info_keeps_zero_id_event_out_of_response_path(board_device):
    connector = BoardConnector(board_device)

    try:
        response = connector.get_board_info(timeout=1.0)
        event = connector.next_event(timeout=1.0)

        assert response.board_name == "Adafruit CLUE"
        assert response.request_id != 0
        assert isinstance(event, SensorSample)
        assert event.request_id == 0
    finally:
        connector.close()
