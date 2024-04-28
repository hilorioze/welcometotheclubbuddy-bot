from contextlib import suppress
from types import ModuleType
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable


import importlib.metadata
from importlib.metadata import Distribution

DEFAULT_DISTRIBUTION_VERSION = "0.0.0"


def get_distribution(distribution_name: str) -> Distribution | None:
    try:
        return importlib.metadata.distribution(distribution_name)
    except (ImportError, ValueError):
        return None


def get_version(
    distribution_name: str | Distribution,
    fallback_distribution: str = DEFAULT_DISTRIBUTION_VERSION,
) -> str:
    distribution: Distribution | None = (
        distribution_name
        if isinstance(distribution_name, Distribution)
        else get_distribution(distribution_name)
    )

    if distribution:
        with suppress(KeyError):
            return distribution.version

    return fallback_distribution


def create_fake_module(**kwargs: Any) -> ModuleType:
    name: str = kwargs.pop("__name__", None) or kwargs.pop("name")
    doc: str | None = kwargs.pop("__doc__", None) or kwargs.pop("doc", None)

    fake_module = ModuleType(name=name, doc=doc)

    for key, value in kwargs.items():
        setattr(fake_module, key, value)

    return fake_module


def copy_module(module: ModuleType) -> ModuleType:
    allowed_module_attributes: Iterable[str] = {
        "__name__",
        "__doc__",
        "__loader__",
        "__package__",
        "__path__",
        "__spec__",
    }
    kwargs: dict[str, Any] = {
        attribute: value
        for attribute in allowed_module_attributes
        if (value := getattr(module, attribute, None))
    }
    return create_fake_module(**kwargs)
