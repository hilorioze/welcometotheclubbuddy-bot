from collections.abc import Sequence
from importlib import import_module
from importlib.util import find_spec
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType


def choice_in_order(
    module_names: Sequence[str],
    default: str | None = None,
) -> "ModuleType":
    """Finds and import an installed module from the list of module names
    :param module_names: list of module names
    :param default: default module name
    :return: Found module.
    """
    default_name = default or module_names[0]
    installed = []
    for module_name in module_names:
        try:
            if find_spec(module_name) is not None:
                installed.append(module_name)
        except ImportError:
            continue

    if not installed and default is None:
        error_msg = "No proper module was installed. List: {}".format(", ".join(module_names))
        raise ModuleNotFoundError(
            error_msg,
        )

    ordered_module_name = installed[-1] if installed else default_name
    return import_module(ordered_module_name)
