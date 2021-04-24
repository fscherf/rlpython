from textwrap import wrap

from rlpython.utils.asyncio_utils import get_all_loops, get_all_tasks
from rlpython.utils.argument_parser import ReplArgumentParser
from rlpython.utils.gc_utils import get_object_by_id
from rlpython.utils.table import write_table
from rlpython.utils.strings import color


class TasksCommand:
    """
    List all running asyncio tasks
    """

    NAME = 'tasks'

    def __init__(self, repl):
        self.repl = repl

    def run(self, argv):
        # parse command line
        argument_parser = ReplArgumentParser(repl=self.repl, prog='tasks')
        argument_parser.add_argument('loop-id', nargs='?')

        arguments = vars(argument_parser.parse_args(argv[1:]))

        # find loops
        if arguments['loop-id']:
            loop = get_object_by_id(arguments['loop-id'])

            if not loop:
                self.repl.write(color('ERROR: invalid loop id\n', fg='red'))

                return 1

            loops = [loop]

        else:
            loops = get_all_loops()

        loops = sorted(loops, key=lambda i: id(i))

        # write table
        rows = [
            ['Loop ID', 'Task ID', 'State', 'Task'],
        ]

        for loop in loops:
            tasks = sorted(get_all_tasks(loop=loop), key=lambda i: id(i))

            for task in tasks:
                rows.append([
                    str(id(loop)),
                    str(id(task)),
                    str(task._state),
                    '\n'.join(wrap(repr(task), 80)),
                ])

        if len(rows) == 1:
            return

        write_table(rows, self.repl.write)
