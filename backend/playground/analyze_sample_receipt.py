"""Playground: map a sample receipt through Document Intelligence into Receipt."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.schemas.receipt import map_receipt_fields
from app.services.document_intelligence_service import DocumentIntelligenceService

BACKEND_DIR = Path(__file__).resolve().parents[1]
SAMPLE_RECEIPT_URL = (
    "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/"
    "master/curl/form-recognizer/contoso-allinone.jpg"
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
    result = service.analyze_document_url("prebuilt-receipt", SAMPLE_RECEIPT_URL)
    fields, confidence = _first_document_fields(result)
    receipt = map_receipt_fields(fields, document_confidence=confidence)
    print(json.dumps(receipt.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    main()
