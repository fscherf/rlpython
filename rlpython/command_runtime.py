import shlex

from rlpython.utils.argument_parser import ReplArgumentParserError
from rlpython.commands.variables import VariablesCommand
from rlpython.commands.threads import ThreadsCommand
from rlpython.commands.tasks import TasksCommand
from rlpython.commands.loops import LoopsCommand
from rlpython.commands.edit import EditCommand

DEFAULT_COMMANDS = [
    VariablesCommand,
    ThreadsCommand,
    TasksCommand,
    LoopsCommand,
    EditCommand,
]


class CommandRuntime:
    def __init__(self, repl):
        self.repl = repl
        self.commands = {}

        for command in DEFAULT_COMMANDS:
            self.install_command(command)

    def shutdown(self):
        pass

    def install_command(self, command_class, name=''):
        command = command_class(self.repl)
        name = name or command.NAME

        self.commands[name] = command

    def validate_source(self, raw_source):
        try:
            shlex.split(raw_source)

            return True

        except Exception:
            return False

    def run(self, raw_source):
        argv = shlex.split(raw_source[1:])
        name = argv[0]

        if name not in self.commands:
            self.repl.write("ERROR: unknown command '{}'\n".format(name))

            return

        try:
            exit_code = self.commands[name].run(argv)

            if exit_code is None:
                exit_code = 0

        except ReplArgumentParserError:
            exit_code = 1

            pass

        except Exception as exception:
            exit_code = 1

            self.repl.write_exception(exception)

        return exit_code
