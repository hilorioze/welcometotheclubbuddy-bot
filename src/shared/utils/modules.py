import asyncio
from contextlib import suppress
from types import ModuleType
from typing import TYPE_CHECKING, Any, cast

from shared.interfaces.json import JSONModule
from shared.tools import choicelib
from shared.utils.python import copy_module

if TYPE_CHECKING:
    from collections.abc import Callable

try:  # pragma: no cover
    import nest_asyncio
except ImportError:  # pragma: no cover
    nest_asyncio = cast(Any, None)

try:  # pragma: no cover
    import uvloop
except ImportError:  # pragma: no cover
    uvloop = cast(Any, None)


def get_loop(*, force_nest_asyncio: bool = False) -> asyncio.AbstractEventLoop:
    is_uvloop_allowed = uvloop and not force_nest_asyncio

    event_loop: asyncio.AbstractEventLoopPolicy = (
        uvloop.EventLoopPolicy() if is_uvloop_allowed else asyncio.DefaultEventLoopPolicy()
    )
    new_loop: asyncio.AbstractEventLoop = event_loop.new_event_loop()

    if nest_asyncio and not is_uvloop_allowed:
        nest_asyncio.apply(new_loop)

    return new_loop


def _json_module_compat(module: ModuleType) -> JSONModule:
    loads: Callable[[str], Any] | None = None
    dumps: Callable[[Any], str] | None = None
    dumps_method: Callable[[Any], Any] | None = None
    loads_method: Callable[[str], Any] | None = None

    patched_json_module = copy_module(module)

    for dumps_method_name in ("dumps", "encode", "dump"):
        dumps_method = getattr(module, dumps_method_name, None)
        if not dumps_method:
            continue

        try:
            result = dumps_method({"a": "b"})
        except (TypeError, ValueError):
            continue

        if isinstance(result, str):
            dumps = dumps_method
        elif isinstance(result, bytes):
            dumps = lambda o: dumps_method(o).decode()  # noqa: E731, B023
        else:
            continue

        break

    if not dumps:
        error_msg = f"Unable to find a valid `dumps` method in {module.__name__}"
        raise RuntimeError(error_msg)

    for loads_method_name in ("loads", "decode", "load"):
        loads_method = getattr(module, loads_method_name, None)
        if not loads_method:
            continue

        try:
            result = loads_method('{"a": "b"}')
        except (TypeError, ValueError):
            continue

        if isinstance(result, dict) and result == {"a": "b"}:
            loads = loads_method
        else:
            continue

        break

    if not loads:
        error_msg = f"Unable to find a valid `loads` method in {module.__name__}"
        raise RuntimeError(error_msg)

    with suppress(AttributeError):  # may be caused by unavailability of setting attribute
        patched_json_module.loads = loads  # type: ignore[attr-defined]

    with suppress(AttributeError):  # may be caused by unavailability of setting attribute
        patched_json_module.dumps = dumps  # type: ignore[attr-defined]

    return cast(JSONModule, patched_json_module)


def get_json() -> JSONModule:
    module: ModuleType = choicelib.choice_in_order(
        module_names=["ujson", "hyperjson", "orjson", "msgspec.json"],
        default="json",
    )
    return cast(JSONModule, _json_module_compat(module))


json: JSONModule = get_json()
