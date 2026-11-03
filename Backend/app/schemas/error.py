"""Error contract shared by every endpoint (see app/core/errors.py)."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class ErrorBody(BaseModel):
    code: str = Field(examples=["invalid_request"], description="Stable code for the frontend (app.core.errors.ErrorCode)")
    message: str = Field(description="Ready to show to the user (Spanish)")
    detail: Any = Field(default=None, description="Extra context, e.g. [{field, message}] for validation errors")
    request_id: Optional[str] = Field(default=None, description="Same value as the X-Request-ID header")


class ErrorResponse(BaseModel):
    error: ErrorBody
