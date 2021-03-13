import inspect

VERSION = (0, 1, 1)
VERSION_STRING = '{}'.format('.'.join([str(i) for i in VERSION]))


def embed(*args, **kwargs):
    from rlpython.repl import Repl

    # use namespace of caller instead of own if nothing is set
    if 'globals' not in kwargs and 'locals' not in kwargs:
        stack = inspect.stack()
        frame_info = stack[1]

        kwargs['globals'] = frame_info.frame.f_globals
        kwargs['locals'] = frame_info.frame.f_locals

    repl = Repl(*args, **kwargs)

    try:
        repl.interact()

    finally:
        repl.write_history()
