from traceback import format_exception
import readline
import json
import sys
import os

from rlpython.runtimes.command_runtime import CommandRuntime
from rlpython.runtimes.python_runtime import PythonRuntime
from rlpython.runtimes.shell_runtime import ShellRuntime
from rlpython.utils.gc_utils import get_object_by_id
from rlpython.templating import TemplatingEngine
from rlpython.completion import Completer
from rlpython.utils.strings import color
from rlpython.aliases import Aliases
from rlpython import VERSION_STRING

DEFAULT_HISTORY_FILE = '~/.rlpython.history'
DEFAULT_HISTORY_SIZE = 1000
DEFAULT_PROMPT_PREFIX = ''
DEFAULT_PROMPT = '>>> '
DEFAULT_PROMPT_PS2 = '... '

DEFAULT_BANNER = """Python {} on {}
rlpython {}
Type '?' for help
""".format(
    sys.version,
    sys.platform,
    VERSION_STRING,
)

DEFAULT_VARIABLES = {
    'pretty_print': True,
    'repeat_last_command_on_enter': False,
}

HELP_TEXT = """
rlpython
========

rlpython is a GNU Readline based Python REPL, fully compatible with
Python's syntax.


Help / Inspection
-----------------

?             Show this help text
object?       Inspect given object
object??      Show help text of given object
%edit object  Open the source code of given object if available
help          Python's builtin help system


REPL Commands
-------------

{commands}
"""


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
                 globals={}, locals={}, commands=[], **variables):

        self.banner = banner
        self.warnings = warnings
        self.prompt_prefix = prompt_prefix
        self.ps1 = prompt
        self.ps2 = prompt_ps2
        self.history_file = os.path.expanduser(history_file)
        self.history_size = history_size
        self.globals = globals
        self.locals = locals

        self.exit_code = 0

        self.variables = {
            **DEFAULT_VARIABLES,
            **variables,
        }

        # setup templating engine
        self.templating_engine = TemplatingEngine(repl=self)

        # setup completion
        self.completer = Completer(repl=self)

        # setup readline
        readline.set_auto_history(False)
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self.complete)
        readline.set_completer_delims(' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>?')

        self.read_history()

        # setup runtimes
        self.python_runtime = PythonRuntime(
            repl=self,
            globals=globals,
            locals=locals,
        )

        self.command_runtime = CommandRuntime(
            repl=self,
        )

        for command in commands:
            self.install_command(command)

        self.shell_runtime = ShellRuntime(
            repl=self,
        )

        # setup aliasses
        self.aliases = Aliases(repl=self)

        # finish
        self.clear_line_buffer()
        self.setup()

    def shutdown(self):
        self.python_runtime.shutdown()
        self.command_runtime.shutdown()

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

    # utils ###################################################################
    def get_object_by_id(self, object_id):
        return get_object_by_id(object_id)

    # commands ################################################################
    def install_command(self, command):
        self.command_runtime.install_command(command)

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

    def write_warning(self, string):
        self.write(color('WARNING: {}'.format(string), fg='yellow'))

    def write_error(self, string):
        self.write(color('ERROR: {}'.format(string), fg='red'))

    # line buffer #############################################################
    def clear_line_buffer(self):
        self.line_buffer = ''

    def validate_line_buffer(self):
        try:
            line_buffer = self.aliases.resolve(self.line_buffer)

            if line_buffer.startswith('%'):
                return self.command_runtime.validate_source(line_buffer)

            elif line_buffer.startswith('!'):
                return self.shell_runtime.validate_source(line_buffer)

            return self.python_runtime.validate_source(line_buffer)

        except Exception as exception:
            self.exit_code = 1

            self.write_exception(exception, prefix='rlpython: ')

            return False

    # I/O #####################################################################
    def write_warnings(self):
        for warning in self.warnings:
            self.write(color('WARNING: {}\n'.format(warning), fg='yellow'))

    def write_banner(self):
        self.write(self.banner)

    def write_help(self):
        text = HELP_TEXT.format(
            commands=self.command_runtime.gen_help_text(),
        )

        self.write(text.strip() + '\n')

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
        line_buffer = readline.get_line_buffer()

        return self.completer.complete(text, state, line_buffer)

    def handle_empty_line(self):
        self.clear_line_buffer()

        if self.variables['repeat_last_command_on_enter']:
            command = self.history[-1]

            self.write(command + '\n')
            self.run(command)

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

            except EOFError:
                self.write('\n')
                return True

            except KeyboardInterrupt:
                self.write('\n')
                return False

    def handle_ctrl_c(self):
        self.clear_line_buffer()
        self.write('^C\n')
        self.exit_code = 1

    def run(self, command):
        try:
            # aliasses
            command = self.aliases.resolve(command)

            # templating
            if self.templating_engine.is_template(command):
                command = self.templating_engine.render(command)
                self.write(command)

            # help
            if command.strip() == '?':
                self.write_help()
                self.exit_code = 0

            # repl commands
            elif command.startswith('%'):
                self.exit_code = self.command_runtime.run(command)

            # shell commands
            elif command.startswith('!'):
                self.exit_code = self.shell_runtime.run(command)

            # python code
            else:
                self.exit_code = self.python_runtime.run(command)

        except Exception as exception:
            self.exit_code = 1

            self.write_exception(exception, prefix='rlpython: ')

        return self.exit_code
