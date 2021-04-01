from asyncio.base_events import BaseEventLoop
import asyncio
import sys

from rlpython.utils.gc_utils import get_objects_by_class


def get_all_tasks(loop):
    if sys.version_info >= (3, 7):
        return asyncio.all_tasks(loop=loop)

    return asyncio.Task.all_tasks(loop=loop)


def get_all_loops():
    return get_objects_by_class(object_class=BaseEventLoop)
