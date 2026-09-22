from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    HARVEST_API_KEY: str = ''
    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_NAME: str = 'postgres'
    DB_USER: str = 'postgres'
    DB_PASSWORD: str = ''


settings = Settings()