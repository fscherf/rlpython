from argparse import ArgumentParser
import signal
import os


def handle_command_line():
    from rlpython.repl_client import ReplClient
    from rlpython import embed

    argument_parser = ArgumentParser(prog='rlpython')

    argument_parser.add_argument('url', nargs='?', type=str)
    argument_parser.add_argument('--history-file', type=str)
    argument_parser.add_argument('--history-size', type=int)
    argument_parser.add_argument('--banner', type=str)
    argument_parser.add_argument('--prompt', type=str)
    argument_parser.add_argument('--prompt-ps2', type=str)
    argument_parser.add_argument('--frontend-mode', action='store_true')

    namespace = argument_parser.parse_args()

    # client mode
    if namespace.url:
        try:
            repl_client = ReplClient(
                url=namespace.url,
                frontend_mode=namespace.frontend_mode,
            )

        except Exception as exception:
            exit(str(exception))

        try:
            repl_client.interact()

        finally:
            repl_client.shutdown()

        exit(0)

    # local mode
    repl_kwargs = {}

    for key, value in vars(namespace).items():

        if key in ('frontend_mode',):
            continue

        if value is None:
            continue

        repl_kwargs[key] = value

    embed(
        globals={},
        single_threaded=True,
        started_from_cmd_line=True,
        **repl_kwargs,
    )


if __name__ == '__main__':
    handle_command_line()
