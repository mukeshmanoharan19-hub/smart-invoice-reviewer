"""Validate that a selected GL code exists in the Northstar catalog."""

from __future__ import annotations

from app.accounting.catalog import GLAccount, get_gl_account


class InvalidGLSelectionError(ValueError):
    """Raised when a suggested or selected GL code is not in the catalog."""


def require_gl_account(code: str | None) -> GLAccount:
    if code is None or not str(code).strip():
        raise InvalidGLSelectionError("A GL account selection is required")
    account = get_gl_account(str(code).strip())
    if account is None:
        raise InvalidGLSelectionError(f"Unknown GL account code: {code}")
    return account
