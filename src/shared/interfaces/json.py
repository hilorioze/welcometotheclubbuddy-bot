from collections.abc import Callable
from typing import Any, Protocol, TypeAlias

JSON_LOADS_METHOD: TypeAlias = Callable[[str], Any]
JSON_DUMPS_METHOD: TypeAlias = Callable[[Any], str]


class JSONModule(Protocol):
    loads: JSON_LOADS_METHOD
    dumps: JSON_DUMPS_METHOD
