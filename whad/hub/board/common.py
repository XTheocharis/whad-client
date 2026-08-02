from queue import Empty, Full, Queue

from whad.hub.message import PbFieldInt, PbMessageWrapper
from whad.protocol.whad_pb2 import Message


class BoardMessage(PbMessageWrapper):
    request_id = PbFieldInt("board.request_id")
    BOARD_FIELD = None
    PAYLOAD_CLS = None

    def __init__(self, message: Message = None, **kwargs):
        board_field = object.__getattribute__(self, "BOARD_FIELD")
        payload_cls = object.__getattribute__(self, "PAYLOAD_CLS")
        if message is None and board_field is not None and payload_cls is not None:
            message = Message()
            getattr(message.board, board_field).CopyFrom(payload_cls())
        super().__init__(message=message, **kwargs)


class BoardConnectorError(Exception):
    pass


class BoardPendingRequestFull(BoardConnectorError):
    pass


class BoardDuplicateRequest(BoardConnectorError):
    pass


class BoardRequestTimeout(BoardConnectorError):
    pass


class BoardEventQueueFull(BoardConnectorError):
    pass


class PendingRequest:
    def __init__(self, request_id, max_responses):
        self.request_id = request_id
        self.responses = Queue(maxsize=max_responses)
        self.terminal_seen = False

    def put(self, message):
        try:
            self.responses.put_nowait(message)
            return True
        except Full:
            return False

    def get(self, timeout=None):
        try:
            return self.responses.get(block=True, timeout=timeout)
        except Empty as err:
            raise BoardRequestTimeout("timed out waiting for Board response") from err
