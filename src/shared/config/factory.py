from typing import Any

from dotenv import find_dotenv

from shared.config.models import Config


def load_from_dotenv_filename(dotenv_filename: str = ".env", **kwargs: Any) -> Config:
    dotenv_file: str | None = find_dotenv(dotenv_filename, raise_error_if_not_found=False)
    return Config(
        _env_file=dotenv_file if dotenv_file else None,
        _env_file_encoding="utf-8",
        **kwargs,
    )
