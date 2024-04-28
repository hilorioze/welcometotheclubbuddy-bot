from jinja2 import Environment

from .factory import create_jinja_environment

_environment: Environment | None = None


async def async_render_text(text: str, /, environment: Environment | None = None, **kwargs) -> str:
    if not environment:
        global _environment  # noqa: PLW0603
        if not _environment:
            _environment = create_jinja_environment()
        environment = _environment

    template = environment.get_template(text)
    if environment.is_async:
        return await template.render_async(**kwargs)
    return template.render(**kwargs)
