"""GL categorization pipeline step: suggest a catalog account from normalized fields."""

from __future__ import annotations

from app.config import Settings, get_settings
from app.pipeline.base import PipelineContext
from app.pipeline.gl_models import GlSuggestion
from app.providers.openai_gl_suggester import OpenAIGLSuggester


class GlCategorizationStep:
    name = "gl_categorization"

    def __init__(
        self,
        categorizer: OpenAIGLSuggester | None = None,
        *,
        settings: Settings | None = None,
    ) -> None:
        resolved = settings or get_settings()
        self._categorizer = categorizer or OpenAIGLSuggester(
            api_key=resolved.openai_api_key,
            model=resolved.openai_model,
        )

    def run(self, ctx: PipelineContext) -> PipelineContext:
        if ctx.review_data is None:
            raise ValueError(
                "GlCategorizationStep requires ctx.review_data from ExtractionStep."
            )
        suggestion = self._categorizer.suggest(ctx.review_data)
        return ctx.model_copy(update={"gl_suggestion": suggestion})


__all__ = ["GlCategorizationStep", "GlSuggestion"]
