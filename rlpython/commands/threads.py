import threading
import sys

from rlpython.utils.argument_parser import ReplArgumentParser
from rlpython.utils.table import write_table


class ThreadsCommand:
    NAME = 'threads'

    def run(self, repl, argv):
        # parse command line
        argument_parser = ReplArgumentParser(repl=repl, prog='threads')

        argument_parser.parse_args(argv[1:])

        # write table
        rows = [['Thread ID', 'Thread Name', 'Alive', 'Daemon', 'Task']]

        current_frames = sys._current_frames()

        for thread in threading.enumerate():
            frame = current_frames[thread.ident]

            task = '{}:{} {}'.format(
                frame.f_code.co_filename,
                frame.f_lineno,
                frame.f_code.co_name,
            )

            rows.append([
                thread.ident,
                thread.getName(),
                thread.isAlive(),
                thread.isDaemon(),
                task,
            ])

        write_table(rows, repl.write)
