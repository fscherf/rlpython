import readline
import socket
import time

from rlpython.repl import Repl

from rlpython.protocol import (
    encode_completion_request_message,
    END_OF_TRANSMISSION,
    encode_ping_message,
    encode_run_message,
    decode_message,
    MESSAGE_TYPE,
)


class ReplClient(Repl):
    def __init__(self, host, port, *args, frontend_mode=False, **kwargs):
        self.host = host
        self.port = port
        self.url = '{}:{}'.format(host, port)

        if frontend_mode:
            prompt_prefix = ''

        else:
            prompt_prefix = '{} '.format(self.url)

        super().__init__(
            *args,
            prompt_prefix=prompt_prefix,
            **kwargs,
        )

    def send_message(self, message):
        exit_code, payload = message

        if not exit_code:
            return

        self.sock.send(payload)

    def recv_message(self):
        message_buffer = bytes()

        while True:
            data = self.sock.recv(1)

            if not data:
                return True, None, None

            message_buffer += data

            if message_buffer[-1] == END_OF_TRANSMISSION[0]:
                exit_code, message_type, payload = decode_message(
                    message_buffer,
                )

                if exit_code:
                    return False, message_type, payload

                message_buffer = bytes()

                continue

    def setup(self):
        # setup socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # wait for connection
        while True:
            try:
                self.sock.connect((self.host, self.port))

                break

            except ConnectionRefusedError:
                time.sleep(1)

        # handle setup messages from server
        while True:
            disconnected, message_type, payload = self.recv_message()

            if disconnected:
                exit(1)

            # set
            if message_type == MESSAGE_TYPE.SET:
                name, value = payload

                if name in ('banner', 'warnings', 'ps1', 'ps2'):
                    setattr(self, name, value)

            # ready
            if message_type == MESSAGE_TYPE.READY:
                break

        self.write_banner()
        self.write_warnings()

    def complete(self, text, state):
        # handle starting tabs in multi line statements locally
        if not text.strip():
            if state == 0:
                readline.insert_text('\t')
                readline.redisplay()

                return ''

            else:
                return None

        # remote completion
        self.send_message(encode_completion_request_message(text, state))

        while True:
            disconnected, message_type, payload = self.recv_message()

            if disconnected:
                exit(1)

            # completion response
            if message_type == MESSAGE_TYPE.COMPLETION_RESPONSE:
                return payload

    def handle_empty_line(self):
        self.clear_line_buffer()

        # send ping to server and wait for pong
        self.send_message(encode_ping_message())

        while True:
            disconnected, message_type, payload = self.recv_message()

            if disconnected:
                exit(1)

            # pong
            if message_type == MESSAGE_TYPE.PONG:
                return

    def run(self, command):
        self.send_message(encode_run_message(command))

        while True:
            disconnected, message_type, payload = self.recv_message()

            if disconnected:
                exit(1)

            # write
            if message_type == MESSAGE_TYPE.WRITE:
                self.write(payload)

            # exit code
            if message_type == MESSAGE_TYPE.EXIT_CODE:
                self.exit_code = payload

                return
