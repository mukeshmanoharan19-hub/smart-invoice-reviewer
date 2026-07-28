"""Azure Document Intelligence extraction surface."""

from __future__ import annotations

from pathlib import Path

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, AnalyzeResult
from azure.core.credentials import AzureKeyCredential


class DocumentIntelligenceService:
    """Thin client wrapper around prebuilt invoice and receipt models."""

    def __init__(self, endpoint: str, api_key: str) -> None:
        self._client = DocumentIntelligenceClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key),
        )

    def analyze_invoice(self, path: Path) -> AnalyzeResult:
        return self._analyze_path("prebuilt-invoice", path)

    def analyze_receipt(self, path: Path) -> AnalyzeResult:
        return self._analyze_path("prebuilt-receipt", path)

    def analyze_document_url(self, model_id: str, url: str) -> AnalyzeResult:
        poller = self._client.begin_analyze_document(
            model_id,
            AnalyzeDocumentRequest(url_source=url),
        )
        return poller.result()

    def _analyze_path(self, model_id: str, path: Path) -> AnalyzeResult:
        with path.open("rb") as document:
            poller = self._client.begin_analyze_document(model_id, document)
        return poller.result()
