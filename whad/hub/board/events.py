from whad.hub.message import PbFieldArray, PbFieldBool, PbFieldBytes, PbFieldInt
from whad.protocol.board import board_pb2 as pb

from .common import BoardMessage
from .domain import BoardDomain
from ..message import pb_bind


@pb_bind(BoardDomain, "sensor_sample", 1)
class SensorSample(BoardMessage):
    BOARD_FIELD = "sensor_sample"
    PAYLOAD_CLS = pb.SensorSample
    sensor_id = PbFieldInt("board.sensor_sample.sensor_id")
    sequence = PbFieldInt("board.sensor_sample.sequence")
    timestamp_us = PbFieldInt("board.sensor_sample.timestamp_us")
    status = PbFieldInt("board.sensor_sample.status")
    values = PbFieldArray("board.sensor_sample.values")


@pb_bind(BoardDomain, "audio_chunk", 1)
class AudioChunk(BoardMessage):
    BOARD_FIELD = "audio_chunk"
    PAYLOAD_CLS = pb.AudioChunk
    sequence = PbFieldInt("board.audio_chunk.sequence")
    offset = PbFieldInt("board.audio_chunk.offset")
    count = PbFieldInt("board.audio_chunk.count")
    pcm = PbFieldBytes("board.audio_chunk.pcm")
    eof = PbFieldBool("board.audio_chunk.eof")
    total = PbFieldInt("board.audio_chunk.total")
    result = PbFieldInt("board.audio_chunk.result")


@pb_bind(BoardDomain, "input_event", 1)
class InputEvent(BoardMessage):
    BOARD_FIELD = "input_event"
    PAYLOAD_CLS = pb.InputEvent
    sequence = PbFieldInt("board.input_event.sequence")
    timestamp_us = PbFieldInt("board.input_event.timestamp_us")
    source = PbFieldInt("board.input_event.source")
    action = PbFieldInt("board.input_event.action")
    value = PbFieldInt("board.input_event.value")


@pb_bind(BoardDomain, "gesture_event", 1)
class GestureEvent(BoardMessage):
    BOARD_FIELD = "gesture_event"
    PAYLOAD_CLS = pb.GestureEvent
    sequence = PbFieldInt("board.gesture_event.sequence")
    timestamp_us = PbFieldInt("board.gesture_event.timestamp_us")
    gesture = PbFieldInt("board.gesture_event.gesture")


@pb_bind(BoardDomain, "log_chunk", 1)
class LogChunk(BoardMessage):
    BOARD_FIELD = "log_chunk"
    PAYLOAD_CLS = pb.LogChunk
    sequence = PbFieldInt("board.log_chunk.sequence")
    cursor = PbFieldInt("board.log_chunk.cursor")
    offset = PbFieldInt("board.log_chunk.offset")
    count = PbFieldInt("board.log_chunk.count")
    data = PbFieldBytes("board.log_chunk.data")
    eof = PbFieldBool("board.log_chunk.eof")
    total = PbFieldInt("board.log_chunk.total")
    result = PbFieldInt("board.log_chunk.result")


@pb_bind(BoardDomain, "board_status", 1)
class BoardStatus(BoardMessage):
    BOARD_FIELD = "board_status"
    PAYLOAD_CLS = pb.BoardStatus
    timestamp_us = PbFieldInt("board.board_status.timestamp_us")
    code = PbFieldInt("board.board_status.code")
    result = PbFieldInt("board.board_status.result")
    resource = PbFieldInt("board.board_status.resource")
    instance = PbFieldInt("board.board_status.instance")
    progress_per_mille = PbFieldInt("board.board_status.progress_per_mille")
    terminal = PbFieldBool("board.board_status.terminal")
    detail = PbFieldBytes("board.board_status.detail")
