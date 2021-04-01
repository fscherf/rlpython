from rlcompleter import Completer as rlCompleter


class Completer:
    def __init__(self, repl):
        self.repl = repl

        self.rlcompleter = rlCompleter(namespace=self.repl.locals)

    def python_complete(self, text, state):
        return self.rlcompleter.complete(text, state)

    def shell_complete(self, text, state):
        candidates = []

        for name in sorted(self.repl.shell_runtime.commands.keys()):
            if name.startswith(text):
                candidates.append(name)

        candidates.append(None)

        return candidates[state]

    def complete(self, text, state, line_buffer):
        try:
            # shell
            if line_buffer.startswith('%'):
                line_buffer = line_buffer[1:]

                return self.shell_complete(
                    text=text,
                    state=state,
                    line_buffer=line_buffer,
                )

            # python
            return self.python_complete(text, state)

        except Exception as e:
            self.repl.write('\n')
            self.repl.write_exception(e, prefix='rlpython: ')
