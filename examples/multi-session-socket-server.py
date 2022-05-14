import asyncio
import os

import rlpython

DEBUG = 'RLPYTHON_DEBUG' in os.environ
loop = asyncio.get_event_loop()
a = [10]


with rlpython.embed(bind='localhost:5000', multi_session=True, debug=DEBUG):
    loop.run_forever()

