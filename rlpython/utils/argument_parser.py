from argparse import ArgumentParser


class ReplArgumentParserError(Exception):
    pass


class ReplArgumentParser(ArgumentParser):
    def __init__(self, repl, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._repl = repl

    def _print_message(self, message, file=None):
        self._repl.write(message)

    def exit(self, status=0, message=None):
        if message:
            self._print_message(message)

        raise ReplArgumentParserError
