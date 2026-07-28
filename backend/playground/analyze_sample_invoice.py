"""Playground: map a sample invoice through Document Intelligence into Invoice."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.schemas.invoice import map_invoice_fields
from app.services.document_intelligence_service import DocumentIntelligenceService

BACKEND_DIR = Path(__file__).resolve().parents[1]
SAMPLE_INVOICE_PATH = (
    BACKEND_DIR.parent / "samples" / "generated" / "invoice-001234567-dia-zota.pdf"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    azure_document_intelligence_endpoint: str
    azure_document_intelligence_key: str


def _first_document_fields(result: object) -> tuple[dict, float | None]:
    payload = result.as_dict()  # type: ignore[attr-defined]
    documents = payload.get("documents") or []
    if not documents:
        return {}, None
    document = documents[0]
    return document.get("fields") or {}, document.get("confidence")


def main() -> None:
    settings = Settings()
    service = DocumentIntelligenceService(
        endpoint=settings.azure_document_intelligence_endpoint,
        api_key=settings.azure_document_intelligence_key,
    )
    result = service.analyze_invoice(SAMPLE_INVOICE_PATH)
    fields, confidence = _first_document_fields(result)
    invoice = map_invoice_fields(fields, document_confidence=confidence)
    print(json.dumps(invoice.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    main()
