import secrets
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, SecretStr
from pydantic_settings import BaseSettings


class BotApiTypeEnum(StrEnum):
    PRODUCTION = "production"
    TEST = "test"
    CUSTOM = "custom"
    LOCAL = "local"

    @classmethod
    def _missing_(cls, value: Any) -> Any:
        for member in cls:
            if isinstance(member, str) and member.casefold() == value.casefold():
                return member
        return None


class BotReceivingUpdateModeEnum(StrEnum):
    POLLING = "polling"
    WEBHOOK = "webhook"

    @classmethod
    def _missing_(cls, value: Any) -> Any:
        for member in cls:
            if isinstance(member, str) and member.casefold() == value.casefold():
                return member
        return None


class BotApiConfig(BaseModel):
    type: str = BotApiTypeEnum.PRODUCTION

    base_url: str | None = None
    file_url: str | None = None


class BotReceivingUpdateConfig(BaseModel):
    mode: BotReceivingUpdateModeEnum = BotReceivingUpdateModeEnum.POLLING

    host: str = "127.0.0.1"
    port: int = 8888
    path: str = "/"

    remote_host: str | None = None
    remote_port: int | None = None
    remote_path: str | None = None

    secret_token: SecretStr = Field(default_factory=secrets.token_urlsafe)

    def build_webhook_url(self) -> str:
        path: str = self.remote_path or self.path
        if path == "/":
            path = ""

        url: HttpUrl = HttpUrl.build(
            scheme="https",
            host=self.remote_host or self.host,
            port=self.remote_port or self.port,
            path=path,
        )
        return url.unicode_string()


class BotConfig(BaseSettings):
    token: SecretStr
    parse_mode: str
