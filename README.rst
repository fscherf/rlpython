rlpython
========

rlpython is a GNU Readline based Python REPL without any external dependencies


Installation
------------

.. code-block:: text

    # pip install rlpython


Starting rlpython from the command line
---------------------------------------

.. code-block:: text

    # rlpython


Starting rlpython from Python code
----------------------------------

.. code-block:: python

    import rlpython

    rlpython.embed()


Attach a rlpython shell over network
-------------------------------------

.. code-block:: python

    import rlpython

    rlpython.embed(bind='localhost:5000')


.. code-block:: text

    # rlpython localhost:5000


Start a multisession shell server
---------------------------------

Server
~~~~~~

.. code-block:: python

    import asyncio

    import rlpython

    loop = asyncio.get_event_loop()

    with rlpython.embed(bind='localhost:5000', multi_session=True):
        loop.run_forever()

.. code-block:: text

    # rlpython localhost:5000
