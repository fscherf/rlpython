from rlpython.utils.argument_parser import ReplArgumentParser
from rlpython.utils.table import write_table


class AliasesCommand:
    """
    Manage REPL aliases
    """

    NAME = 'alias'

    def __init__(self, repl):
        self.repl = repl

    def run(self, argv):
        # parse command line
        argument_parser = ReplArgumentParser(repl=self.repl, prog='alias')
        argument_parser.add_argument('name', nargs='?')

        arguments = argument_parser.parse_args(argv[1:])

        # print all variables
        if not arguments.name:
            table = [
                ['Name', 'Value'],
            ]

            for name, value in self.repl.aliases.aliases.items():
                table.append([
                    name,
                    value,
                ])

            write_table(table, self.repl.write)

            return 0

        # print variable
        if '=' not in arguments.name:
            self.repl.write(
                self.repl.aliases.aliases.get(arguments.name, ' ') + '\n')

            return 0

        # set variable
        name, value = arguments.name.split('=', 1)
        self.repl.aliases.aliases[name] = value

        return 0
