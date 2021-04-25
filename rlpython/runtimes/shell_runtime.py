import subprocess
import shlex
import os

from rlpython.utils.argument_parser import (
    ReplArgumentParserError,
    ReplArgumentParser,
)


class ShellRuntime:
    def __init__(self, repl):
        self.repl = repl
        self._old_pwd = os.getcwd()

    def validate_source(self, raw_source):
        try:
            shlex.split(raw_source)

            return True

        except Exception:
            return False

    def change_directory(self, command_line):
        argument_parser = ReplArgumentParser(repl=self.repl, prog='cd')
        argument_parser.add_argument('directory', nargs='?')

        arguments = argument_parser.parse_args(command_line[1:])
        directory = arguments.directory

        if directory == '-':
            directory = self._old_pwd

        else:
            if not directory:
                directory = os.environ.get('HOME', '/home')

            directory = os.path.abspath(directory)

        self._old_pwd = os.getcwd()

        try:
            os.chdir(directory)

        except FileNotFoundError:
            self.repl.write_error(
                'cd: {}: No such file or directory\n'.format(directory),
            )

            return 1

        self.repl.write('{}\n'.format(directory))

        return 0

    def run(self, raw_source):
        # split into command line
        source = raw_source[1:]
        command_line = shlex.split(source)

        # change_directory command
        if command_line[0] == 'cd':
            try:
                return self.change_directory(command_line)

            except ReplArgumentParserError:
                return 1

        # run command
        try:
            output = subprocess.check_output(
                command_line,
                stderr=subprocess.PIPE,
                shell=False,
            ).decode()

            exit_code = 0

        except FileNotFoundError:
            output = ''
            exit_code = 1

            self.repl.write_error(
                '{}: command not found\n'.format(command_line[0]),
            )

        except subprocess.CalledProcessError as exception:
            output = '{}{}'.format(
                exception.output.decode(),
                exception.stderr.decode(),
            )

            exit_code = exception.returncode

        if output:
            self.repl.write(output)

        return exit_code
