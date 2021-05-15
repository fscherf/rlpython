from copy import copy

DEFAULT_ALIASES = {
    'l': '!ls -hlF --color',
    'll': '!ls -hAlF --color',
    'pwd': '!pwd',
    'cd': '!cd',
    '..': '!cd ..',
    'touch': '!touch',
    'mkdir': '!mkdir',
    'cat': '!cat',
    'rm': '!rm',
}


class Aliases:
    def __init__(self, repl):
        self.repl = repl

        self.aliases = copy(DEFAULT_ALIASES)

    def resolve(self, command):
        # check for name collisions with repl variables
        if '=' in command:
            return command

        _command = command.strip()

        if(_command in self.repl.globals or
           _command in self.repl.locals):

            return command

        # resolve aliases
        for name, value in self.aliases.items():
            if not command.startswith(name):
                continue

            if(len(command) >= len(name) and
               command[len(name)] in (' ', '\n', '\t')):

                return '{}{}'.format(value, command[len(name):])

        return command
