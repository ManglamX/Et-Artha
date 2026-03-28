from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "ET Artha"
    app_version: str = "1.0.0"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    frontend_url: str = "http://localhost:3000"
    environment: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
