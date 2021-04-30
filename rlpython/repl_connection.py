from rlpython.logging import SilentLogger
from rlpython.repl import Repl

from rlpython.protocol import (
    encode_completion_response_message,
    encode_exit_code_message,
    encode_ready_message,
    encode_write_message,
    encode_pong_message,
    END_OF_TRANSMISSION,
    encode_set_message,
    decode_message,
    MESSAGE_TYPE,
)

logger = SilentLogger('rlpython.server')


class SocketRepl(Repl):
    def __init__(self, connection, address, **repl_kwargs):
        self.connection = connection
        self.address = address

        super().__init__(**repl_kwargs)

    def send(self, data):
        logger.debug(
            'sending: %s',
            repr(data),
        )

        self.connection.send(data)

    def write_message(self, message):
        exit_code, payload = message

        if not exit_code:
            return

        self.send(payload)

    def setup(self):
        self.write_message(encode_set_message('banner', self.banner))
        self.write_message(encode_set_message('warnings', self.warnings))
        self.write_message(encode_set_message('ps1', self.ps1))
        self.write_message(encode_set_message('ps2', self.ps2))
        self.write_message(encode_ready_message())

    def write(self, string):
        self.write_message(encode_write_message(string))

    def run(self, command):
        exit_code = super().run(command)

        self.write_message(encode_exit_code_message(exit_code))


class ReplConnection:
    def __init__(self, repl_server, connection, address, repl_domain,
                 **repl_kwargs):

        self.repl_server = repl_server
        self.connection = connection
        self.address = address
        self.repl_domain = repl_domain

        self.repl = SocketRepl(
            connection=self.connection,
            address=self.address,
            **repl_kwargs,
        )

        self.repl.set_domain(self.repl_domain)

    def shutdown(self):
        self.repl.shutdown()

    def handle_message(self, raw_message):
        message_is_valid, message_type, payload = decode_message(raw_message)

        logger.debug(
            '%s message received: %s',
            'valid' if message_is_valid else 'invalid',
            raw_message,
        )

        if not message_is_valid:
            return

        # ping (empty line)
        if message_type == MESSAGE_TYPE.PING:
            if self.repl.variables['repeat_last_command_on_enter']:
                command = self.repl.history[-1]

                self.repl.write(command + '\n')
                self.repl.run(command)

            self.repl.write_message(encode_pong_message())

        # run
        elif message_type == MESSAGE_TYPE.RUN:
            self.repl.run(payload)

        # completion request
        elif message_type == MESSAGE_TYPE.COMPLETION_REQUEST:
            text, state, line_buffer = payload

            response = self.repl.completer.complete(text, state, line_buffer)

            self.repl.write_message(
                encode_completion_response_message(response),
            )

    def run_single_threaded(self):
        message_buffer = bytes()

        while True:
            data = self.connection.recv(1)

            if not data:
                break

            message_buffer += data

            if message_buffer[-1] == END_OF_TRANSMISSION[0]:
                self.handle_message(message_buffer)
                message_buffer = bytes()

                continue
