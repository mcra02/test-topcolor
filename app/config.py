from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    app_name: str = "FastAPI Application"
    debug: bool = False
    version: str = "1.0.0"
    hubspot_api_key: str
    http_host: str = "http://localhost:8000"  # Default development host
    subdomain: str = "topcolor"
    domain: str = "cebralab.com"

    beca_object_id: str = "2-43416319"

    class Config:
        env_file = ".env"


settings = Settings()
