from pprint import pformat

from rlpython.utils.argument_parser import ReplArgumentParser
from rlpython.utils.table import write_table
from rlpython.utils.strings import color


class SetCommand:
    NAME = 'set'

    def run(self, repl, argv):
        # parse command line
        argument_parser = ReplArgumentParser(repl=repl, prog='set')
        argument_parser.add_argument('variable', nargs='?')

        arguments = argument_parser.parse_args(argv[1:])

        # print all variables
        if not arguments.variable:
            table = [
                ['Name', 'Value'],
            ]

            for key, value in repl.variables.items():
                table.append([
                    str(key),
                    pformat(value),
                ])

            write_table(table, repl.write)

            return 0

        # print variable
        if '=' not in arguments.variable:
            repl.write(repr(repl.variables.get(arguments.variable, '')) + '\n')

            return 0

        # set variable
        name, value = arguments.variable.split('=')

        try:
            value = repl.python_runtime.eval(value, safe=False)

        except Exception:
            repl.write(
                color(
                    "ERROR: '{}' is no valid python expression\n".format(value),  # NOQA
                    fg='red',
                ),
            )

            return 1

        repl.variables[name] = value
