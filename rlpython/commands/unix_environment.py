import textwrap
import os

from rlpython.utils.argument_parser import ReplArgumentParser
from rlpython.utils.table import write_table
from rlpython.utils.strings import color


class UnixEnvironmentCommand:
    """
    List Unix environmet variables; Print value of given environmet variable
    """

    NAME = 'env'

    def __init__(self, repl):
        self.repl = repl

    def complete(self, text, state, line_buffer):
        names = [*sorted(os.environ.keys())]
        candidates = []

        for name in names:
            if name.startswith(text):
                candidates.append(name)

        candidates.append(None)

        return candidates[state]

    def run(self, argv):
        # parse command line
        argument_parser = ReplArgumentParser(repl=self.repl, prog='env')
        argument_parser.add_argument('name', nargs='?')

        arguments = vars(argument_parser.parse_args(argv[1:]))

        # name
        if arguments['name']:

            # set
            if '=' in arguments['name']:
                name, value = arguments['name'].split('=')

                try:
                    value = self.repl.python_runtime.eval(
                        source=repr(value),
                        safe=False,
                    )

                except Exception:
                    self.repl.write(
                        color(
                            "ERROR: '{}' is no valid python expression\n".format(value),  # NOQA
                            fg='red',
                        ),
                    )

                    return 1

                os.environ[name] = value

            # get
            else:
                self.repl.write(
                    repr(os.environ.get(arguments['name'], '')) + '\n')

            return

        # write table
        rows = [
            ['Key', 'Value'],
        ]

        for key in sorted(os.environ.keys()):
            value = '\n'.join(textwrap.wrap(os.environ[key], 80))

            rows.append([key, value])

        write_table(rows, self.repl.write)
