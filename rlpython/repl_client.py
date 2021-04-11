from tempfile import NamedTemporaryFile
import readline
import socket
import time
import os

from rlpython.utils.editor import run_editor
from rlpython.utils.url import parse_url
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
    def __init__(self, url, *args, frontend_mode=False, **kwargs):
        self.url = url

        self.scheme, self.host, self.port = parse_url(url)

        # setup prompt prefix
        if frontend_mode:
            prompt_prefix = ''

        else:
            if self.scheme == 'file':
                prompt_prefix = 'file://{} '.format(self.host)

            else:
                prompt_prefix = '{}:{} '.format(self.host, self.port)

        super().__init__(
            *args,
            prompt_prefix=prompt_prefix,
            **kwargs,
        )

    def send_message(self, message):
        exit_code, payload = message

        if not exit_code:
            return

        try:
            self.sock.send(payload)

        except BrokenPipeError:
            pass

    def recv_message(self):
        message_buffer = bytes()

        while True:
            try:
                data = self.sock.recv(1)

            except BrokenPipeError:
                return True, None, None

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
        # network
        if self.scheme == 'rlpython':
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connect_arg = (self.host, self.port)

        # unix domain socket
        elif self.scheme == 'file':
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            connect_arg = self.host

        # wait for connection
        while True:
            try:
                self.sock.connect(connect_arg)

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
        line_buffer = readline.get_line_buffer()

        # handle starting tabs in multi line statements locally
        if not line_buffer.strip() and not text.strip():
            if state == 0:
                readline.insert_text('\t')
                readline.redisplay()

                return ''

            return None

        # remote completion
        self.send_message(
            encode_completion_request_message(text, state, line_buffer)
        )

        while True:
            disconnected, message_type, payload = self.recv_message()

            if disconnected:
                exit(1)

            # write
            if message_type == MESSAGE_TYPE.WRITE:
                self.write(payload)

            # completion response
            elif message_type == MESSAGE_TYPE.COMPLETION_RESPONSE:
                return payload

    def handle_empty_line(self):
        self.clear_line_buffer()

        # send ping to server and wait for pong
        self.send_message(encode_ping_message())

        while True:
            disconnected, message_type, payload = self.recv_message()

            if disconnected:
                exit(1)

            # write
            if message_type == MESSAGE_TYPE.WRITE:
                self.write(payload)

            # pong
            if message_type == MESSAGE_TYPE.PONG:
                return

    def edit(self, filename, lineno, text):
        if text is not None:
            temp_file = NamedTemporaryFile(suffix='.py')
            filename = temp_file.name

            with open(filename, 'w') as f:
                f.write(text)
                f.close()

            filename = temp_file.name

        run_editor(filename=filename, lineno=lineno)

    def run(self, command):
        self.send_message(encode_run_message(command))

        while True:
            disconnected, message_type, payload = self.recv_message()

            if disconnected:
                exit(1)

            # write
            if message_type == MESSAGE_TYPE.WRITE:
                self.write(payload)

            # edit
            elif message_type == MESSAGE_TYPE.EDIT:
                filename, lineno, text = payload

                self.edit(filename, lineno, text)

            # exit code
            elif message_type == MESSAGE_TYPE.EXIT_CODE:
                self.exit_code = payload

                return
