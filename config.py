from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int 
    db_path: str 
    port: int 

    class Config:
        env_file = ".env"

settings = Settings()
