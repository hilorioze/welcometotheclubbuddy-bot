from typing import TYPE_CHECKING, Any, TypeAlias

from jinja2 import Environment

from shared.utils.jinja.loaders.stub import StubLoader

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping

    FilterType: TypeAlias = Callable[..., str]
    FiltersType: TypeAlias = Iterable[tuple[str, FilterType]] | Mapping[str, FilterType]


def create_jinja_environment(
    *args: Any,
    filters: "FiltersType | None" = None,
    **kwargs: Any,
) -> Environment:
    kwargs.setdefault("autoescape", True)
    kwargs.setdefault("lstrip_blocks", True)
    kwargs.setdefault("trim_blocks", True)
    if "loader" not in kwargs:
        kwargs["loader"] = StubLoader()

    env = Environment(*args, **kwargs)  # noqa: S701  we already specified this in kwargs

    if filters is not None:
        env.filters.update(filters)

    return env
