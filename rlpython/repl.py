#!/usr/bin/env python
# -*- coding: utf-8 -*-

from traceback import format_exception
import readline
import json
import sys
import os

from rlpython.python_runtime import PythonRuntime
from rlpython.shell_runtime import ShellRuntime
from rlpython.utils.color import color
from rlpython import VERSION_STRING

DEFAULT_HISTORY_FILE = '~/.rlpython.history'
DEFAULT_HISTORY_SIZE = 1000
DEFAULT_PROMPT = '>>> '
DEFAULT_PROMPT_PS2 = '... '

DEFAULT_BANNER = """Python {} on {}
rlpython {}
""".format(
    sys.version,
    sys.platform,
    VERSION_STRING,
)


class Repl:
    def __init__(self, banner=DEFAULT_BANNER, prompt=DEFAULT_PROMPT,
                 prompt_ps2=DEFAULT_PROMPT_PS2,
                 history_file=DEFAULT_HISTORY_FILE,
                 history_size=DEFAULT_HISTORY_SIZE,
                 globals={}, locals={}):

        self.banner = banner
        self.ps1 = prompt
        self.ps2 = prompt_ps2
        self.history_file = os.path.expanduser(history_file)
        self.history_size = history_size

        self.exit_code = 0

        # setup readline
        readline.set_auto_history(False)
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self.complete)

        self.read_history()

        # setup runtimes
        self.python_runtime = PythonRuntime(
            repl=self,
            globals=globals,
            locals=locals,
        )

        self.shell_runtime = ShellRuntime(
            repl=self,
        )

        # finish
        self.clear_line_buffer()
        self.setup()

    # history #################################################################
    def read_history(self):
        self.history = []
        readline.clear_history()

        try:
            for line in open(self.history_file, 'r'):
                item = json.loads(line)
                self.add_history(item)

        except Exception:
            pass

    def add_history(self, item):
        # skip duplicates
        if self.history and item == self.history[-1]:
            return

        self.history.append(item)

        # rotate history
        self.history = self.history[self.history_size*-1:]

        for item in self.history:
            readline.add_history(item)

    def write_history(self):
        try:
            with open(self.history_file, 'w+') as f:
                for item in self.history:
                    f.write(json.dumps(item) + '\n')

        except Exception:
            pass

    # error management ########################################################
    def write_exception(self, exception, prefix=''):
        lines = format_exception(
            etype=type(exception),
            value=exception,
            tb=exception.__traceback__,
        )

        text = ''.join(lines)

        if prefix:
            lines = text.splitlines()

            for index, line in enumerate(lines):
                lines[index] = prefix + line

            text = '\n'.join(lines) + '\n'

        self.write(color(text, color='red'))

    # line buffer #############################################################
    def clear_line_buffer(self):
        self.line_buffer = ''

    def _validate_line_buffer(self):
        if self.line_buffer.startswith('%'):
            return self.shell_runtime.validate_source(self.line_buffer)

        return self.python_runtime.validate_source(self.line_buffer)

    def _gen_prompt(self):
        prompt_color = 'green'

        if self.exit_code != 0:
            prompt_color = 'red'

        ps1 = color(
            self.ps1,
            color=prompt_color,
            style='bright',
        )

        ps2 = color(
            self.ps2,
            color=prompt_color,
            style='normal',
        )

        if not self.line_buffer:
            return ps1

        if self._validate_line_buffer():
            return ps1

        return ps2

    def embed(self):
        while True:
            try:
                self.line_buffer += input(self._gen_prompt()) + '\n'

                # handle empty lines
                if not self.line_buffer.strip():
                    self.clear_line_buffer()

                    continue

            except KeyboardInterrupt:
                self.handle_ctrl_c()

                continue

            except EOFError:
                self.handle_ctrl_d()

                return

            # emulated CTRL-C
            if self.line_buffer.strip().endswith('!'):
                self.handle_ctrl_c()

                continue

            # multi line
            if not self._validate_line_buffer():
                continue

            self.add_history(self.line_buffer.strip())
            self.run()
            self.clear_line_buffer()

    # application code ########################################################
    def write(self, string):
        print(string, end='')

    def setup(self):
        self.write(self.banner)

    def complete(self, text, state):
        return self.python_runtime.complete(text, state)

    def handle_ctrl_d(self):
        self.write('^D\n')

    def handle_ctrl_c(self):
        self.exit_code = 1
        self.write('^C\n')

        self.clear_line_buffer()

    def run(self):
        try:
            if self.line_buffer.startswith('%'):
                self.exit_code = self.shell_runtime.run(self.line_buffer)

            else:
                self.exit_code = self.python_runtime.run(self.line_buffer)

        except Exception as exception:
            self.exit_code = 1

            self.write_exception(exception, prefix='rlpython: ')
