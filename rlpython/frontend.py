from threading import Thread
import sys
import os


def start_frontend(port):
    def _run():
        os.system(
            '{} -m rlpython.command_line localhost:{} --frontend'.format(
                sys.executable,
                port,
            ),
        )

    thread = Thread(
        name='rlpython Frontend',
        daemon=False,
        target=_run,
    )

    thread.start()

    return thread

