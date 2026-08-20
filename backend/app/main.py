"""FastAPI application construction and dependency wiring."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.accounting.routes import create_accounting_router
from app.config import ensure_data_dirs, get_app_config, get_settings
from app.database import build_database
from app.documents.models import HealthOut
from app.documents.repository import DocumentRepository, init_database
from app.documents.routes import create_document_router
from app.documents.service import DocumentService


def create_app() -> FastAPI:
    settings = get_settings()
    config = ensure_data_dirs(get_app_config())
    engine, session_factory = build_database(config.database_url)
    init_database(engine)
    repository = DocumentRepository(session_factory)
    service = DocumentService(settings=settings, config=config, repository=repository)

    app = FastAPI(title="Invoice Review API", version="0.1.0")
    app.state.config = config
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[config.allowed_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(create_document_router(service))
    app.include_router(create_accounting_router(service))

    @app.get("/health", response_model=HealthOut)
    def health() -> HealthOut:
        return HealthOut()

    return app
