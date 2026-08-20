"""Validation pipeline step: deterministic Northstar policy as plain Python."""

from __future__ import annotations

from collections.abc import Callable

from app.config import AppConfig, get_app_config
from app.document_review.review_fields import ReviewFields
from app.documents.validation import validate_document
from app.pipeline.base import PipelineContext

DuplicateChecker = Callable[[ReviewFields], bool]


class ValidationStep:
    name = "validation"

    def __init__(
        self,
        *,
        config: AppConfig | None = None,
        duplicate_checker: DuplicateChecker | None = None,
    ) -> None:
        self._config = config or get_app_config()
        self._duplicate_checker = duplicate_checker

    def run(self, ctx: PipelineContext) -> PipelineContext:
        if ctx.review_data is None:
            raise ValueError("ValidationStep requires ctx.review_data from ExtractionStep.")

        duplicate = False
        if self._duplicate_checker is not None:
            duplicate = self._duplicate_checker(ctx.review_data)

        selected_gl = None
        if ctx.gl_suggestion is not None:
            selected_gl = ctx.gl_suggestion.account_code.value

        issues = validate_document(
            ctx.review_data,
            duplicate_exists=duplicate,
            selected_gl_code=selected_gl,
            config=self._config,
        )
        return ctx.model_copy(update={"issues": issues})
