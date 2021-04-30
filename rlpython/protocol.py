from rlpython.logging import SilentLogger
import json

logger = SilentLogger('rlpython.protocol')

END_OF_TRANSMISSION = bytes([4])
MESSAGE_TYPES = range(1, 11)


class MESSAGE_TYPE:
    PING = 1
    PONG = 2
    SET = 3
    READY = 4
    COMPLETION_REQUEST = 5
    COMPLETION_RESPONSE = 6
    RUN = 7
    WRITE = 8
    EXIT_CODE = 9
    EDIT = 10


def encode_message(raw_message):
    try:
        message = json.dumps(raw_message)

        return True, message.encode() + END_OF_TRANSMISSION

    except Exception:
        logger.error(
            'exception raised while encoding %s',
            repr(raw_message),
            exc_info=True,
        )

        return False, None


def decode_message(raw_message):
    try:
        if raw_message[-1] == END_OF_TRANSMISSION[0]:
            raw_message = raw_message[:-1]

        message_type, payload = json.loads(raw_message.decode())

    except Exception:
        logger.error(
            'exception raised while decoding %s',
            repr(raw_message),
            exc_info=True,
        )

        return False, None, None

    if message_type not in MESSAGE_TYPES:
        logger.error('invalid message type: %s', repr(message_type))

        return False, None, None

    return True, message_type, payload


def encode_ping_message():
    return encode_message([MESSAGE_TYPE.PING, None])


def encode_pong_message():
    return encode_message([MESSAGE_TYPE.PONG, None])


def encode_set_message(name, value):
    return encode_message([MESSAGE_TYPE.SET, [name, value]])


def encode_ready_message():
    return encode_message([MESSAGE_TYPE.READY, None])


def encode_completion_request_message(text, state, line_buffer):
    return encode_message(
        [MESSAGE_TYPE.COMPLETION_REQUEST, [text, state, line_buffer]],
    )


def encode_completion_response_message(return_value):
    return encode_message([MESSAGE_TYPE.COMPLETION_RESPONSE, return_value])


def encode_run_message(command):
    return encode_message([MESSAGE_TYPE.RUN, command])


def encode_write_message(string):
    return encode_message([MESSAGE_TYPE.WRITE, string])


def encode_keyboard_interrupt_message():
    return encode_message([MESSAGE_TYPE.EXIT_CODE, None])


def encode_exit_code_message(exit_code):
    return encode_message([MESSAGE_TYPE.EXIT_CODE, exit_code])


def encode_edit_message(filename, lineno, encode_text=False):
    text = None

    if encode_text:
        text = open(filename, 'r').read()

    return encode_message([MESSAGE_TYPE.EDIT, [filename, lineno, text]])
