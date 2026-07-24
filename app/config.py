"""Runtime configuration for the agent runner."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "info"

    # The MCP server this runner calls for on-chain tools.
    mcp_url: str = "http://mcp:3333"
    backend_url: str = "http://backend:3000"

    # Model credentials. Blank locally; injected from the secrets manager on deploy.
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    max_steps: int = 8

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    def validate_for_production(self) -> list[str]:
        if not self.is_production:
            return []
        missing = []
        if not (self.anthropic_api_key or self.openai_api_key):
            missing.append("ANTHROPIC_API_KEY or OPENAI_API_KEY")
        return missing


@lru_cache
def get_settings() -> Settings:
    return Settings()
