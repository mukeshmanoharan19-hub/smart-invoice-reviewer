"""HTTP routes for document upload, review, and decisions."""

from __future__ import annotations

from typing import Annotated, NoReturn

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.documents.models import (
    AccountingUpdateRequest,
    CorrectionEmailOut,
    DecisionRequest,
    DocumentDetail,
    DocumentSummary,
    DocumentUpdateRequest,
)
from app.documents.service import DocumentService, DocumentServiceError

UploadFileParam = Annotated[UploadFile, File()]


def create_document_router(service: DocumentService) -> APIRouter:
    router = APIRouter(prefix="/api/documents", tags=["documents"])

    def _http_error(exc: DocumentServiceError) -> NoReturn:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    @router.get("", response_model=list[DocumentSummary])
    def list_documents() -> list[DocumentSummary]:
        return service.list_documents()

    @router.post("", response_model=DocumentDetail)
    def create_document(file: UploadFileParam) -> DocumentDetail:
        try:
            payload = file.file.read()
            return service.create_document(
                filename=file.filename or "upload.bin",
                content_type=file.content_type or "application/octet-stream",
                payload=payload,
            )
        except DocumentServiceError as exc:
            _http_error(exc)

    @router.get("/{document_id}", response_model=DocumentDetail)
    def get_document(document_id: str) -> DocumentDetail:
        try:
            return service.get_document(document_id)
        except DocumentServiceError as exc:
            _http_error(exc)

    @router.get("/{document_id}/file")
    def get_document_file(document_id: str) -> FileResponse:
        try:
            path, content_type, filename = service.get_stored_file(document_id)
            return FileResponse(path, media_type=content_type, filename=filename)
        except DocumentServiceError as exc:
            _http_error(exc)

    @router.put("/{document_id}", response_model=DocumentDetail)
    def update_document(document_id: str, body: DocumentUpdateRequest) -> DocumentDetail:
        try:
            return service.update_fields(document_id, body.fields)
        except DocumentServiceError as exc:
            _http_error(exc)

    @router.put("/{document_id}/accounting", response_model=DocumentDetail)
    def update_accounting(
        document_id: str,
        body: AccountingUpdateRequest,
    ) -> DocumentDetail:
        try:
            return service.update_accounting(document_id, body.gl_account_code)
        except DocumentServiceError as exc:
            _http_error(exc)

    @router.post("/{document_id}/decision", response_model=DocumentDetail)
    def decide_document(document_id: str, body: DecisionRequest) -> DocumentDetail:
        try:
            return service.decide(document_id, body.decision)
        except DocumentServiceError as exc:
            _http_error(exc)

    @router.post("/{document_id}/correction-email", response_model=CorrectionEmailOut)
    def correction_email(document_id: str) -> CorrectionEmailOut:
        try:
            return service.draft_correction_email(document_id)
        except DocumentServiceError as exc:
            _http_error(exc)

    @router.delete("/{document_id}", status_code=204)
    def delete_document(document_id: str) -> None:
        try:
            service.delete_document(document_id)
        except DocumentServiceError as exc:
            _http_error(exc)

    return router
