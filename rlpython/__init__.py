import inspect

VERSION = (0, 2)
VERSION_STRING = '{}'.format('.'.join([str(i) for i in VERSION]))


def embed(frontend=False, bind='', started_from_cmd_line=False, **repl_kwargs):
    from rlpython.repl import Repl

    # use namespace of caller instead of own if nothing is set
    if 'globals' not in repl_kwargs and 'locals' not in repl_kwargs:
        stack = inspect.stack()
        frame_info = stack[1]

        repl_kwargs['globals'] = frame_info.frame.f_globals
        repl_kwargs['locals'] = frame_info.frame.f_locals

    # bind mode
    if bind:
        raise NotImplementedError

    # frontend mode
    elif frontend:
        raise NotImplementedError

    # non frontend mode
    else:
        if not started_from_cmd_line:
            if 'warnings' not in repl_kwargs:
                repl_kwargs['warnings'] = []

            repl_kwargs['warnings'].append(
                'running without frontend (Use "!" instead of CTRL-C)')

        repl = Repl(**repl_kwargs)

        try:
            repl.interact()

        finally:
            repl.write_history()
