from collections.abc import Sequence

import sentry_sdk
from sentry_sdk.integrations import Integration

DEFAULT_PACKAGE_NAME = "unnamed"


def format_release(package_name: str, version: str) -> str:
    return f"{package_name or DEFAULT_PACKAGE_NAME}@{version}"


def initialize_sentry(
    sentry_dsn: str | None = None,
    sentry_environment: str | None = None,
    *,
    release: str | None = None,
    integrations: Sequence[Integration],
    traces_sample_rate: float = 1.0,
    profiles_sample_rate: float = 1.0,
) -> None:
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=sentry_environment,
            release=release,
            integrations=integrations,
            traces_sample_rate=traces_sample_rate,
            profiles_sample_rate=profiles_sample_rate,
        )
