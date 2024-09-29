import functools
import threading
from collections.abc import Callable
from typing import TypeVar

__all__ = ("thread_local_cached",)

_T = TypeVar("_T")


def thread_local_cached(func: Callable[[], _T], /) -> Callable[[], _T]:
    thread_local = threading.local()
    functools.wraps(func)

    def wrapped() -> _T:
        try:
            return thread_local.value
        except AttributeError:
            thread_local.value = result = func()
            return result

    return wrapped
