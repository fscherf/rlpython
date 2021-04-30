import inspect
import logging
import os


def embed(single_threaded=False, bind='', permissions='600',
          multi_session=False, started_from_cmd_line=False, print=print,
          debug=False, **repl_kwargs):

    from rlpython.frontend import start_frontend
    from rlpython.repl_server import ReplServer
    from rlpython.repl import Repl

    # debug mode
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        os.environ['RLPYTHON_DEBUG'] = 'True'

    # use namespace of caller instead of own if nothing is set
    if 'globals' not in repl_kwargs and 'locals' not in repl_kwargs:
        stack = inspect.stack()
        frame_info = stack[1]

        repl_kwargs['globals'] = frame_info.frame.f_globals
        repl_kwargs['locals'] = frame_info.frame.f_locals

    # setup warnings
    if 'warnings' not in repl_kwargs:
        repl_kwargs['warnings'] = []

    if not started_from_cmd_line:
        repl_kwargs['warnings'].append('running single threaded: cancellation using CTRL-C will not work')  # NOQA

    if single_threaded and not bind and not started_from_cmd_line:
        repl_kwargs['warnings'].append('running single threaded: Use "!" to cancel multi line statements')  # NOQA

    # network embed
    if bind:
        single_threaded = True  # FIXME

        # single threaded
        if single_threaded:
            repl_server = ReplServer(
                url=bind,
                permissions=permissions,
                repl_domain=Repl.DOMAIN.NETWORK,
                print=print,
                **repl_kwargs,
            )

            if multi_session:
                return repl_server

            try:
                repl_server.setup()
                repl_server.print_bind_informations()
                repl_server.run_single_session(**repl_kwargs)

            except OSError as exception:
                exit('rlpython: ERROR: {}'.format(exception.args[1]))

            finally:
                repl_server.shutdown()

        # multi threaded
        else:
            raise NotImplementedError

    # local embed
    else:

        # single threaded
        if single_threaded:
            repl = Repl(**repl_kwargs)

            try:
                repl.interact()

            finally:
                repl.shutdown()

        # multi threaded
        else:
            repl_server = ReplServer(
                url='localhost:0',
                permissions=permissions,
                repl_domain=Repl.DOMAIN.LOCAL_NETWORK,
            )

            repl_server.setup()
            port = repl_server.get_port()

            start_frontend(port)

            repl_server.run_single_session(**repl_kwargs)
