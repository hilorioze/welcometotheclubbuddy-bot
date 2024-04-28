import sys
from asyncio import Future
from collections.abc import Awaitable, Coroutine, Generator
from typing import Any, TypeAlias, TypeVar

T = TypeVar("T")

if sys.version_info >= (3, 12):
    AwaitableLike: TypeAlias = Awaitable[T]
    CoroutineLike: TypeAlias = Coroutine[Any, Any, T]
else:
    AwaitableLike: TypeAlias = Generator[Any, None, T] | Awaitable[T]
    CoroutineLike: TypeAlias = Generator[Any, None, T] | Coroutine[Any, Any, T]

FutureLike: TypeAlias = Future[T] | Generator[Any, None, T] | Awaitable[T]
