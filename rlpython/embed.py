import inspect


def embed(single_threaded=False, bind='', started_from_cmd_line=False,
          print=print, **repl_kwargs):

    from rlpython.frontend import start_frontend
    from rlpython.repl_server import ReplServer
    from rlpython.utils.url import parse_url
    from rlpython.repl import Repl

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
            host, port = parse_url(bind)

            repl_server = ReplServer(
                host=host,
                port=port,
                repl_domain=Repl.DOMAIN.NETWORK,
            )

            try:
                repl_server.setup()

                print('rlpython: running on {}:{}'.format(host, repl_server.get_port()))  # NOQA

                repl_server.run_single_threaded(**repl_kwargs)

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
                repl_domain=Repl.DOMAIN.LOCAL_NETWORK,
            )

            repl_server.setup()
            port = repl_server.get_port()

            start_frontend(port)

            repl_server.run_single_threaded(**repl_kwargs)
