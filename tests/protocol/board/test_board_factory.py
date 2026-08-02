from whad.hub import Domain as HubDomain, ProtocolHub
from whad.hub.board import BoardDomain, BoardInfoResponse, Commands, GetBoardInfoRequest
from whad.hub.discovery import Capability, Domain


def test_board_domain_is_registered_in_both_domain_enums():
    assert HubDomain.BOARD == "board"
    assert Domain.Board == 0x0C000000
    assert Capability.Read == 0x100
    assert Capability.Write == 0x200
    assert Capability.Stream == 0x400
    assert Capability.Store == 0x800


def test_get_board_info_request_factory_sets_request_id_and_oneof():
    hub = ProtocolHub()
    msg = hub.board.create_get_board_info(request_id=7)

    assert isinstance(msg, GetBoardInfoRequest)
    assert msg.request_id == 7
    assert msg.message.board.WhichOneof("msg") == "get_board_info"
    assert Commands.GetBoardInfo == 0


def test_board_info_response_parses_through_domain_dispatch():
    factory = BoardDomain(1)
    msg = factory.create_board_info_response(
        request_id=9,
        board_name="Adafruit CLUE",
        hardware_revision="rev-a",
        firmware_version="0.1.0",
        protocol_variant="board-v1",
        device_id=b"CLUE",
        active_runtime=1,
        implemented_sensor_count=14,
    )

    parsed = BoardDomain.parse(1, msg.message)

    assert isinstance(parsed, BoardInfoResponse)
    assert parsed.request_id == 9
    assert parsed.board_name == "Adafruit CLUE"
    assert parsed.implemented_sensor_count == 14
