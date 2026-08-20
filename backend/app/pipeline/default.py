"""Assemble the default document-review pipeline chain."""

from __future__ import annotations

from collections.abc import Callable

from app.config import AppConfig, Settings, get_app_config, get_settings
from app.document_review.review_fields import ReviewFields
from app.pipeline.base import Pipeline
from app.pipeline.classification import ClassificationStep, DocumentClassifier
from app.pipeline.document_review import DocumentReviewStep
from app.pipeline.extraction import ExtractionStep
from app.pipeline.gl_categorization import GlCategorizationStep
from app.pipeline.validation import DuplicateChecker, ValidationStep
from app.providers.openai_document_extractor import OpenAIDocumentExtractor
from app.providers.openai_gl_suggester import OpenAIGLSuggester


def build_default_pipeline(
    *,
    settings: Settings | None = None,
    config: AppConfig | None = None,
    duplicate_checker: DuplicateChecker | Callable[[ReviewFields], bool] | None = None,
    classifier: DocumentClassifier | None = None,
    extractor: OpenAIDocumentExtractor | None = None,
    gl_suggester: OpenAIGLSuggester | None = None,
) -> Pipeline:
    """Classify → extract → stamp provenance → suggest GL → validate."""

    resolved_settings = settings or get_settings()
    resolved_config = config or get_app_config()
    return Pipeline(
        [
            ClassificationStep(classifier or DocumentClassifier(settings=resolved_settings)),
            ExtractionStep(extractor, settings=resolved_settings),
            DocumentReviewStep(),
            GlCategorizationStep(gl_suggester, settings=resolved_settings),
            ValidationStep(config=resolved_config, duplicate_checker=duplicate_checker),
        ]
    )
