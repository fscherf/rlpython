from rlcompleter import Completer as rlCompleter
from itertools import chain
from glob import glob
import os


class Namespace(dict):
    def __init__(self, locals, globals):
        self.locals = locals
        self.globals = globals

    def items(self):
        return chain(
            self.locals.items(),
            self.globals.items(),
        )

    def __getitem__(self, name):
        if name in self.locals:
            return self.locals[name]

        if name in self.globals:
            return self.globals[name]

        raise KeyError


class Completer:
    def __init__(self, repl):
        self.repl = repl

        self.rlcompleter = rlCompleter(
            namespace=Namespace(
                locals=self.repl.locals,
                globals=self.repl.globals,
            ),
        )

    def python_complete(self, text, state):
        return self.rlcompleter.complete(text, state)

    def command_complete(self, text, state, line_buffer):
        # run custom completion
        if ' ' in line_buffer:
            command_name = line_buffer.split(' ', 1)[0]

            if(command_name and
               command_name in self.repl.command_runtime.commands):

                command = self.repl.command_runtime.commands[command_name]

                if hasattr(command, 'complete'):
                    return command.complete(text, state, line_buffer)

        # complete from command_runtime.commands
        candidates = []

        for name in sorted(self.repl.command_runtime.commands.keys()):
            if name.startswith(text):
                candidates.append(name)

        candidates.append(None)

        return candidates[state]

    def file_complete(self, text, state, line_buffer):
        path = os.path.normpath(text)

        if os.path.isdir(path) and path != '/':
            path += '/'

        candidates = []

        for candidate in glob(path + '*'):
            candidate = os.path.normpath(candidate)

            if os.path.isdir(candidate):
                candidate += '/'

            if candidate not in candidates:
                candidates.append(candidate)

        candidates.sort()
        candidates.append(None)

        return candidates[state]

    def complete(self, text, state, line_buffer):
        try:
            line_buffer = self.repl.aliases.resolve(line_buffer + '\n')

            # commands
            if line_buffer.startswith('%'):
                line_buffer = line_buffer[1:]

                return self.command_complete(
                    text=text,
                    state=state,
                    line_buffer=line_buffer,
                )

            # shell
            elif line_buffer.startswith('!'):
                return self.file_complete(
                    text=text,
                    state=state,
                    line_buffer=line_buffer,
                )

            # python
            return self.python_complete(text, state)

        except Exception as e:
            self.repl.write('\n')
            self.repl.write_exception(e, prefix='rlpython: ')
