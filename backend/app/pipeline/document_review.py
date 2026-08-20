"""Stamp OpenAI provenance on extracted review fields.

Without Document Intelligence, there is no hybrid merge. This step still records
where each value came from so Maya can see openai vs human sources.
"""

from __future__ import annotations

from app.document_review.provenance import stamp_openai_sources
from app.pipeline.base import PipelineContext


class DocumentReviewStep:
    name = "document_review"

    def run(self, ctx: PipelineContext) -> PipelineContext:
        if ctx.review_data is None:
            raise ValueError("DocumentReviewStep requires ctx.review_data from ExtractionStep.")
        stamped = stamp_openai_sources(ctx.review_data)
        return ctx.model_copy(update={"review_data": stamped})
