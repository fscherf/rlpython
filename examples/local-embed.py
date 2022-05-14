import os

import rlpython

DEBUG = 'RLPYTHON_DEBUG' in os.environ
a = [10]


def function():
    b = [20]

    rlpython.embed(debug=DEBUG)


function()

print('a:', a)
