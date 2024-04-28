from collections.abc import Callable

from jinja2 import BaseLoader, Environment


class StubLoader(BaseLoader):
    def get_source(
        self,
        environment: Environment,
        template: str,
    ) -> tuple[str, str | None, Callable[[], bool]]:
        del environment  # unusable
        return template, template, lambda: True
