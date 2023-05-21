import rlpython

from rlpython.utils.argument_parser import ReplArgumentParser
from rlpython.utils.table import write_table

USER = {
    'alice': 'Alice Allison',
    'ally': 'Ally Allison',
    'bob': 'Bob Roberts',
    'carl': 'Carl Carlson',
    'mal': 'Malory Masterson'
}


class UserListCommand:
    """
    Show User list
    """

    NAME = 'user'

    def __init__(self, repl):
        self.repl = repl

    def complete(self, text, state, line_buffer):
        names = sorted(list(USER.keys()))
        candidates = []

        for name in names:
            if name.startswith(text):
                candidates.append(name)

        candidates.append(None)

        return candidates[state]

    def run(self, argv):

        # parse command line arguments
        # ReplArgumentParser is a subclass of argparse.ArgumentParser
        argument_parser = ReplArgumentParser(
            repl=self.repl,
            prog=self.NAME,
        )

        argument_parser.add_argument('username', nargs='?')
        argument_parser.add_argument('-l', '--limit', type=int)

        args = argument_parser.parse_args(argv[1:])

        # show given user
        if args.username:
            if args.username not in USER:
                self.repl.write(
                    f"no user with username '{args.username}' found\n",
                )

                return 1

            # we use repl.write instead of print here, so the command
            # also works over the network
            self.repl.write(f"{USER[args.username]}\n")

        # show all user
        else:
            rows = [['Username', 'Full Name']]

            for index, (user_name, full_name) in enumerate(USER.items()):
                rows.append(
                    [user_name, full_name],
                )

                if args.limit and args.limit == index + 1:
                    break

            write_table(rows, self.repl.write)


rlpython.embed(commands=[UserListCommand])
