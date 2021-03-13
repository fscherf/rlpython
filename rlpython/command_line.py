from argparse import ArgumentParser
import signal
import os


def handle_command_line():
    from rlpython import embed

    argument_parser = ArgumentParser(prog='rlpython')

    argument_parser.add_argument('--history-file', type=str)
    argument_parser.add_argument('--history-size', type=int)
    argument_parser.add_argument('--banner', type=str)
    argument_parser.add_argument('--prompt', type=str)
    argument_parser.add_argument('--prompt-ps2', type=str)
    argument_parser.add_argument('--frontend-mode', action='store_true')

    namespace = argument_parser.parse_args()

    repl_kwargs = {}

    for key in dir(namespace):
        if key.startswith('_'):
            continue

        if key in ('frontend_mode'):
            continue

        value = getattr(namespace, key)

        if value is None:
            continue

        repl_kwargs[key] = value

    if namespace.frontend_mode:
        def restore_pgrp(*args, **kwargs):
            os.tcsetpgrp(fd, old_pgrp)
            os.setpgid(0, old_pgrp)

            exit(0)

        signal.signal(signal.SIGTSTP, signal.SIG_IGN)
        signal.signal(signal.SIGTTOU, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, restore_pgrp)

        pid = os.getpid()
        fd = os.open('/dev/tty', os.O_RDONLY)
        old_pgrp = os.tcgetpgrp(fd)

        os.setpgid(0, pid)
        os.tcsetpgrp(fd, pid)

    try:
        embed(
            globals={},
            locals={},
            started_from_cmd_line=True,
            **repl_kwargs,
        )

    finally:
        if namespace.frontend_mode:
            restore_pgrp()


if __name__ == '__main__':
    handle_command_line()
