"""Provider settings and fixed Northstar application configuration."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BACKEND_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
DATABASE_PATH = DATA_DIR / "documents.db"

MAX_UPLOAD_BYTES = 4 * 1024 * 1024
ALLOWED_CONTENT_TYPES = frozenset(
    {
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/jpg",
    }
)
NORTHSTAR_CUSTOMER_NAME = "Northstar Facilities Pvt. Ltd."
NORTHSTAR_CUSTOMER_GSTIN = "29AABCN2082N1Z3"
EXPECTED_CURRENCY = "INR"
AMOUNT_TOLERANCE = Decimal("0.01")
LOW_CONFIDENCE_THRESHOLD = 0.80


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Immutable tutorial policy that does not come from the environment."""

    max_upload_bytes: int = MAX_UPLOAD_BYTES
    allowed_content_types: frozenset[str] = ALLOWED_CONTENT_TYPES
    northstar_customer_name: str = NORTHSTAR_CUSTOMER_NAME
    northstar_customer_gstin: str = NORTHSTAR_CUSTOMER_GSTIN
    expected_currency: str = EXPECTED_CURRENCY
    amount_tolerance: Decimal = AMOUNT_TOLERANCE
    low_confidence_threshold: float = LOW_CONFIDENCE_THRESHOLD
    data_dir: Path = DATA_DIR
    uploads_dir: Path = UPLOADS_DIR
    database_path: Path = DATABASE_PATH
    allowed_origin: str = "http://localhost:5173"

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.database_path}"


class Settings(BaseSettings):
    """Provider credentials read from backend/.env."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = Field(min_length=1)
    openai_model: str = Field(min_length=1)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


@lru_cache(maxsize=1)
def get_app_config() -> AppConfig:
    return AppConfig()


def ensure_data_dirs(config: AppConfig | None = None) -> AppConfig:
    cfg = config or get_app_config()
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    cfg.uploads_dir.mkdir(parents=True, exist_ok=True)
    return cfg
