"""HTTP routes for the fixed Northstar GL catalog."""

from __future__ import annotations

from fastapi import APIRouter

from app.documents.models import GLAccountOut
from app.documents.service import DocumentService


def create_accounting_router(service: DocumentService) -> APIRouter:
    router = APIRouter(prefix="/api/accounting", tags=["accounting"])

    @router.get("/gl-accounts", response_model=list[GLAccountOut])
    def get_gl_accounts() -> list[GLAccountOut]:
        return service.list_gl_accounts()

    return router
