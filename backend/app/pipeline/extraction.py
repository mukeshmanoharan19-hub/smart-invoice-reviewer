"""Extraction pipeline step: route field extraction by classified document kind."""

from __future__ import annotations

from app.config import Settings, get_settings
from app.pipeline.base import PipelineContext
from app.pipeline.classification_models import DocumentKind
from app.providers.openai_document_extractor import OpenAIDocumentExtractor


class ExtractionStep:
    name = "extraction"

    def __init__(
        self,
        extractor: OpenAIDocumentExtractor | None = None,
        *,
        settings: Settings | None = None,
    ) -> None:
        resolved = settings or get_settings()
        self._extractor = extractor or OpenAIDocumentExtractor(
            api_key=resolved.openai_api_key,
            model=resolved.openai_model,
        )

    def run(self, ctx: PipelineContext) -> PipelineContext:
        if ctx.classification is None:
            raise ValueError("ExtractionStep requires ctx.classification from ClassificationStep.")

        fields = self._extractor.extract(
            ctx.document_path,
            ctx.content_type,
            document_kind=ctx.classification.document_kind,
            classification_confidence=ctx.classification.confidence,
        )
        if ctx.classification.document_kind == DocumentKind.receipt:
            fields = fields.model_copy(update={"document_type": "receipt"})
        else:
            fields = fields.model_copy(update={"document_type": "invoice"})
        return ctx.model_copy(update={"review_data": fields})
