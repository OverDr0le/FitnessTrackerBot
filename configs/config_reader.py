from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    weather_api: SecretStr
    run_param: bool = False
    db_lite: SecretStr
    WEBHOOK_HOST: str
    WEBHOOK_PATH: str
    WEBAPP_HOST: str
    WEBAPP_PORT: int

    
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()