#!/usr/bin/env python
# -*- coding: utf-8 -*-

from traceback import format_exception
import readline
import json
import sys
import os

from rlpython.python_runtime import PythonRuntime
from rlpython.shell_runtime import ShellRuntime
from rlpython.utils.strings import color
from rlpython import VERSION_STRING

DEFAULT_HISTORY_FILE = '~/.rlpython.history'
DEFAULT_HISTORY_SIZE = 1000
DEFAULT_PROMPT_PREFIX = ''
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
    class DOMAIN:
        LOCAL = 1
        NETWORK = 2
        LOCAL_NETWORK = 3

    def __init__(self, banner=DEFAULT_BANNER, warnings=[],
                 prompt_prefix=DEFAULT_PROMPT_PREFIX,
                 prompt=DEFAULT_PROMPT,
                 prompt_ps2=DEFAULT_PROMPT_PS2,
                 history_file=DEFAULT_HISTORY_FILE,
                 history_size=DEFAULT_HISTORY_SIZE,
                 globals={}, locals={}):

        self.banner = banner
        self.warnings = warnings
        self.prompt_prefix = prompt_prefix
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

    def shutdown(self):
        self.python_runtime.shutdown()
        self.shell_runtime.shutdown()

        if self.domain == self.DOMAIN.LOCAL:
            self.write_history()

    # domain ##################################################################
    @property
    def domain(self):
        if not hasattr(self, '_domain'):
            self._domain = self.DOMAIN.LOCAL

        return self._domain

    def set_domain(self, domain):
        self._domain = domain

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

        self.write(color(text, fg='red'))

    # line buffer #############################################################
    def clear_line_buffer(self):
        self.line_buffer = ''

    def validate_line_buffer(self):
        if self.line_buffer.startswith('%'):
            return self.shell_runtime.validate_source(self.line_buffer)

        return self.python_runtime.validate_source(self.line_buffer)

    # I/O #####################################################################
    def write_warnings(self):
        for warning in self.warnings:
            self.write(color('WARNING: {}\n'.format(warning), fg='yellow'))

    def write_banner(self):
        self.write(self.banner)

    def gen_prompt(self):
        prompt_color = 'green'

        if self.exit_code != 0:
            prompt_color = 'red'

        ps1 = color(
            self.prompt_prefix + self.ps1,
            fg=prompt_color,
            style='bright',
        )

        ps2 = color(
            self.prompt_prefix + self.ps2,
            fg=prompt_color,
            style='normal',
        )

        if not self.line_buffer:
            return ps1

        if self.validate_line_buffer():
            return ps1

        return ps2

    def interact(self):
        while True:
            try:
                self.line_buffer += input(self.gen_prompt()) + '\n'

                # handle empty lines
                if not self.line_buffer.strip():
                    self.handle_empty_line()

                    continue

            except KeyboardInterrupt:
                self.handle_ctrl_c()

                continue

            except EOFError:
                if self.handle_ctrl_d():
                    return

                continue

            # emulated CTRL-C
            if self.line_buffer.strip().endswith('!'):
                self.handle_ctrl_c()

                continue

            # multi line
            if not self.validate_line_buffer():
                continue

            self.add_history(self.line_buffer.strip())
            self.run(self.line_buffer)
            self.clear_line_buffer()

    # application code ########################################################
    def write(self, string):
        print(string, end='')

    def setup(self):
        self.write_banner()
        self.write_warnings()

    def complete(self, text, state):
        rl_line_buffer = readline.get_line_buffer()

        if rl_line_buffer.startswith('%'):
            rl_line_buffer = rl_line_buffer[1:]

            return self.shell_runtime.complete(
                text=text,
                state=state,
                line_buffer=rl_line_buffer,
            )

        else:
            return self.python_runtime.complete(text, state)

    def handle_empty_line(self):
        self.clear_line_buffer()

    def handle_ctrl_d(self):
        self.clear_line_buffer()
        self.write('\n')

        while True:
            try:
                answer = input('Do you really want to exit ([y]/n)? ')
                answer = answer.strip().lower()

                if answer in ('y', ''):
                    return True

                if answer == 'n':
                    return False

            except(EOFError, KeyboardInterrupt):
                self.write('\n')

                return False

    def handle_ctrl_c(self):
        self.clear_line_buffer()
        self.write('^C\n')
        self.exit_code = 1

    def run(self, command):
        try:
            if command.startswith('%'):
                self.exit_code = self.shell_runtime.run(command)

            else:
                self.exit_code = self.python_runtime.run(command)

        except Exception as exception:
            self.exit_code = 1

            self.write_exception(exception, prefix='rlpython: ')

        return self.exit_code
