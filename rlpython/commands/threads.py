import threading
import traceback
import sys

from rlpython.utils.argument_parser import ReplArgumentParser
from rlpython.utils.table import write_table
from rlpython.utils.strings import color


class ThreadsCommand:
    NAME = 'threads'

    def complete(self, text, state, line_buffer):
        names = []

        for thread in threading.enumerate():
            names.append(str(thread.getName()))

        candidates = []

        for name in sorted(names):
            if name.startswith(text):
                candidates.append(name)

        candidates.append(None)

        return candidates[state]

    def find_frame(self, identifier):
        for thread in threading.enumerate():
            if(str(thread.ident) == identifier or
               thread.getName() == identifier):

                return thread, sys._current_frames()[thread.ident]

        return None, None

    def run(self, repl, argv):
        # parse command line
        argument_parser = ReplArgumentParser(repl=repl, prog='threads')
        argument_parser.add_argument('identifier', nargs='?')

        arguments = vars(argument_parser.parse_args(argv[1:]))

        # show stack of given thread
        if arguments['identifier']:
            thread, frame = self.find_frame(arguments['identifier'])

            if not thread:
                repl.write(color('ERROR: invalid thread ident\n', fg='red'))

                return 1

            repl.write('STACK: {} id={}\n'.format(
                thread.getName(),
                str(thread.ident),
            ))

            for line in traceback.format_stack(frame):
                repl.write(line)

            repl.write('END STACK\n')

            return 0

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
