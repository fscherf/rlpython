from pprint import pformat

from rlpython.utils.argument_parser import ReplArgumentParser
from rlpython.utils.table import write_table
from rlpython.utils.strings import color


class VariablesCommand:
    """
    List, read and write REPL variables
    """

    NAME = 'var'

    def __init__(self, repl):
        self.repl = repl

    def complete(self, text, state, line_buffer):
        names = []
        candidates = []

        for key in sorted(self.repl.variables.keys()):
            value = self.repl.variables[key]

            names.append('{}={}'.format(key, repr(value)))

        for name in names:
            if name.startswith(text):
                candidates.append(name)

        candidates.append(None)

        return candidates[state]

    def run(self, argv):
        # parse command line
        argument_parser = ReplArgumentParser(repl=self.repl, prog='vars')
        argument_parser.add_argument('variable', nargs='?')

        arguments = argument_parser.parse_args(argv[1:])

        # print all variables
        if not arguments.variable:
            table = [
                ['Name', 'Value'],
            ]

            for key, value in self.repl.variables.items():
                table.append([
                    str(key),
                    pformat(value),
                ])

            write_table(table, self.repl.write)

            return 0

        # print variable
        if '=' not in arguments.variable:
            self.repl.write(
                repr(self.repl.variables.get(arguments.variable, '')) + '\n')

            return 0

        # set variable
        name, value = arguments.variable.split('=')

        try:
            value = self.repl.python_runtime.eval(value, safe=False)

        except Exception:
            self.repl.write(
                color(
                    "ERROR: '{}' is no valid python expression\n".format(value),  # NOQA
                    fg='red',
                ),
            )

            return 1

        self.repl.variables[name] = value
