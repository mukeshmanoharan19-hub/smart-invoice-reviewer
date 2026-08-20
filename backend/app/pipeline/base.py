"""Pipeline engine: immutable context, step protocol, and ordered runner."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, ConfigDict

from app.document_review.review_fields import ReviewFields
from app.documents.validation import Issue
from app.pipeline.classification_models import DocumentClassification
from app.pipeline.gl_models import GlSuggestion

logger = logging.getLogger(__name__)


class PipelineContext(BaseModel):
    """Shared state passed through each pipeline step.

    Steps never mutate the context they receive; each returns an updated copy.
    Fields start as None and fill in as the document moves through the chain.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    document_path: Path
    content_type: str
    classification: DocumentClassification | None = None
    review_data: ReviewFields | None = None
    issues: list[Issue] | None = None
    gl_suggestion: GlSuggestion | None = None


class PipelineStep(Protocol):
    name: str

    def run(self, ctx: PipelineContext) -> PipelineContext: ...


class Pipeline:
    """Ordered runner over pipeline steps."""

    def __init__(self, steps: Sequence[PipelineStep]) -> None:
        self.steps = list(steps)

    def run(self, document_path: Path, *, content_type: str) -> PipelineContext:
        ctx = PipelineContext(document_path=document_path, content_type=content_type)
        for index, step in enumerate(self.steps, start=1):
            logger.info("[%d/%d] Starting step: %s", index, len(self.steps), step.name)
            ctx = step.run(ctx)
        return ctx
