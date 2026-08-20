"""First pipeline step: classify the upload as invoice or receipt."""

from __future__ import annotations

from pathlib import Path

from app.config import Settings, get_settings
from app.pipeline.base import PipelineContext
from app.pipeline.classification_models import DocumentClassification, DocumentKind
from app.providers.openai_document_classifier import OpenAIDocumentClassifier

MEDIA_TYPES: dict[str, str] = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


def media_type_for_path(document_path: Path) -> str:
    media_type = MEDIA_TYPES.get(document_path.suffix.lower())
    if media_type is None:
        raise ValueError(
            f"Unsupported document type for {document_path.name}; "
            "expected PDF, PNG, or JPEG"
        )
    return media_type


class DocumentClassifier:
    """LLM classifier that decides invoice vs receipt before extraction."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        provider: OpenAIDocumentClassifier | None = None,
    ) -> None:
        resolved = settings or get_settings()
        self._provider = provider or OpenAIDocumentClassifier(
            api_key=resolved.openai_api_key,
            model=resolved.openai_model,
        )

    def run(self, document_path: Path, content_type: str | None = None) -> DocumentClassification:
        resolved_type = content_type or media_type_for_path(document_path)
        return self._provider.classify(document_path, resolved_type)


class ClassificationStep:
    """Thin pipeline wrapper: classify, then return an updated context copy."""

    name = "classification"

    def __init__(self, classifier: DocumentClassifier | None = None) -> None:
        self._classifier = classifier or DocumentClassifier()

    def run(self, ctx: PipelineContext) -> PipelineContext:
        classification = self._classifier.run(ctx.document_path, ctx.content_type)
        return ctx.model_copy(update={"classification": classification})


__all__ = [
    "ClassificationStep",
    "DocumentClassification",
    "DocumentClassifier",
    "DocumentKind",
    "MEDIA_TYPES",
    "media_type_for_path",
]
