import threading

from rlpython.utils.asyncio_utils import get_all_loops, get_all_tasks
from rlpython.utils.argument_parser import ReplArgumentParser
from rlpython.utils.table import write_table


class LoopsCommand:
    """
    List all running asyncio Loops
    """

    NAME = 'loops'

    def __init__(self, repl):
        self.repl = repl

    def run(self, argv):
        # parse command line
        argument_parser = ReplArgumentParser(repl=self.repl, prog='loops')

        argument_parser.parse_args(argv[1:])

        # write table
        rows = [
            ['Loop ID', 'Thread ID', 'Thread Name', 'Running', 'Task Count'],
        ]

        threads = list(threading.enumerate())

        for loop in get_all_loops():
            thread = ''

            for _thread in threads:
                if _thread.ident == loop._thread_id:
                    thread = _thread.getName()

            rows.append([
                repr(id(loop)),
                loop._thread_id,
                thread,
                loop.is_running(),
                len(get_all_tasks(loop=loop)),
            ])

        if len(rows) == 1:
            return

        write_table(rows, self.repl.write)
