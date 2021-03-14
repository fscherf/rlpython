import subprocess
import sys


def start_frontend(port):
    process = subprocess.Popen([
        sys.executable,
        '-m',
        'rlpython.command_line',
        'localhost:{}'.format(port),
        '--frontend',
    ])

    return process
