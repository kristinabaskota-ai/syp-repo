import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Search for .env in current dir, backend/, or parent directory
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()


class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "RareRoot Plant Marketplace")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "rareroot-super-secret-development-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./rareroot.db")
    DEV_RETURN_RESET_TOKEN: bool = os.getenv("DEV_RETURN_RESET_TOKEN", "true").lower() in ("true", "1", "yes")
    DEFAULT_COUNTRY: str = os.getenv("DEFAULT_COUNTRY", "Nepal")
    CURRENCY: str = os.getenv("CURRENCY", "NPR")

    @property
    def cors_origins(self) -> list[str]:
        raw = os.getenv("CORS_ORIGINS", '["*"]')
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass
        return ["*"]


settings = Settings()
