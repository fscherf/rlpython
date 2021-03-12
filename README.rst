rlpython
========

rlpython is a GNU Readline based Python REPL without any external dependencies


Examples
--------

.. code-block:: text

    >>> import arpgarse
    >>> argparse.ArgumentParser
    <class 'argparse.ArgumentParser'>

    # inspect a python object
    >>> argparse.ArgumentParser.add_argument?
           id: 0x7f3046435a70
         type: <class 'function'>
         file: /home/fsc/.pyenv/versions/3.7.9/lib/python3.7/argparse.py:1328
    signature: add_argument(self, *args, **kwargs)

    # print docstring of a python object
    >>> argparse.ArgumentParser.add_argument??
    add_argument(dest, ..., name=value, ...)
    add_argument(option_string, option_string, ..., name=value, ...)

    # open the source code of a python object in your local editor
    %edit argparse.ArgumentParser.add_argument


Installation
------------

.. code-block:: text

    # pip install rlpython
    # rlpython


Starting rlpython from a Python script
--------------------------------------

.. code-block:: python

    import rlpython

    rlpython.embed()