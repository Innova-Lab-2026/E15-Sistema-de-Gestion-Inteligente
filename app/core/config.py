from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="InobaLab TECBA API", alias="APP_NAME")
    app_env: str = Field(default="local", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="CORS_ORIGINS",
    )

    database_url: str = Field(
        default="postgresql+asyncpg://tecba:tecba@localhost:5432/tecba",
        alias="DATABASE_URL",
    )

    llm_base_url: str = Field(default="", alias="LLM_BASE_URL")
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_model: str = Field(default="gemini-2.0-flash", alias="LLM_MODEL")
    llm_timeout_seconds: int = Field(default=30, alias="LLM_TIMEOUT_SECONDS")

    geocoder_provider: str = Field(default="mock", alias="GEOCODER_PROVIDER")
    geocoder_base_url: str = Field(
        default="https://servicios.usig.buenosaires.gob.ar",
        alias="GEOCODER_BASE_URL",
    )
    geocoder_ws_base_url: str = Field(
        default="https://ws.usig.buenosaires.gob.ar",
        alias="GEOCODER_WS_BASE_URL",
    )
    geocoder_timeout_seconds: int = Field(
        default=10, alias="GEOCODER_TIMEOUT_SECONDS"
    )

    epok_provider: str = Field(default="epok", alias="EPOK_PROVIDER")
    epok_base_url: str = Field(
        default="https://epok.buenosaires.gob.ar",
        alias="EPOK_BASE_URL",
    )
    epok_timeout_seconds: int = Field(default=15, alias="EPOK_TIMEOUT_SECONDS")

    ba_data_base_url: str = Field(
        default="https://data.buenosaires.gob.ar",
        alias="BA_DATA_BASE_URL",
    )
    ba_data_timeout_seconds: int = Field(
        default=30, alias="BA_DATA_TIMEOUT_SECONDS"
    )
    ba_data_user_agent: str = Field(
        default="Mozilla/5.0 (compatible; InobaLab-TECBA/1.0)",
        alias="BA_DATA_USER_AGENT",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
