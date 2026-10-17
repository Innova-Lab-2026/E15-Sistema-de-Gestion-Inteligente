"""Error handling for the whole API: error codes, AppError and global handlers.

Every error response has the same shape (app.schemas.error.ErrorResponse):
    {"error": {"code": "invalid_request", "message": "...", "detail": ..., "request_id": "..."}}
The frontend branches on `code`; `message` is ready to show to the user.

Raise `AppError(ErrorCode.X, detail)` from any layer instead of HTTPException or try/except in
routes. To add a case, add the code to ErrorCode and its (status, message) to ERROR_CATALOG.
"""

from __future__ import annotations

import logging
import time
import uuid
from enum import StrEnum
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings
from app.core.logging import request_id_var
from app.schemas.error import ErrorBody, ErrorResponse

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"
_MAX_CLIENT_REQUEST_ID = 64


class ErrorCode(StrEnum):
    INVALID_REQUEST = "invalid_request"
    NOT_FOUND = "not_found"
    METHOD_NOT_ALLOWED = "method_not_allowed"
    REQUEST_TOO_LARGE = "request_too_large"
    RATE_LIMITED = "rate_limited"
    INTERNAL_ERROR = "internal_error"


# code -> (HTTP status, message for the user)
ERROR_CATALOG: dict[ErrorCode, tuple[int, str]] = {
    ErrorCode.INVALID_REQUEST: (422, "Revisa los datos enviados."),
    ErrorCode.NOT_FOUND: (404, "El recurso solicitado no existe."),
    ErrorCode.METHOD_NOT_ALLOWED: (405, "Metodo no permitido para este recurso."),
    ErrorCode.REQUEST_TOO_LARGE: (413, "La solicitud es demasiado grande."),
    ErrorCode.RATE_LIMITED: (429, "Hay muchas consultas en poco tiempo. Espera un momento y vuelve a intentar."),
    ErrorCode.INTERNAL_ERROR: (
        500,
        "Ocurrio un error inesperado. Si se repite, informalo con el codigo de referencia.",
    ),
}


class AppError(Exception):
    """Expected application error. Raise it anywhere; the handler builds the response."""

    def __init__(
        self,
        code: ErrorCode,
        detail: Any = None,
        *,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.code = code
        self.detail = detail
        self.headers = headers
        super().__init__(f"{code}: {detail}")


def error_response(
    request: Request,
    code: ErrorCode,
    detail: Any = None,
    *,
    status: int | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """Status and message come from ERROR_CATALOG; `status` only keeps an HTTPException's own status."""
    catalog_status, message = ERROR_CATALOG[code]
    body = ErrorResponse(
        error=ErrorBody(
            code=code,
            message=message,
            detail=detail,
            request_id=getattr(request.state, "request_id", None),
        )
    )
    return JSONResponse(body.model_dump(), status_code=status or catalog_status, headers=headers)


# --- Handlers -----------------------------------------------------------------

async def _app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.warning("%s %s -> %s %s", request.method, request.url.path, exc.code, exc.detail or "")
    return error_response(request, exc.code, exc.detail, headers=exc.headers)


_VALIDATION_MESSAGES = {
    "missing": "Campo obligatorio.",
    "string_too_short": "Debe tener al menos {min_length} caracteres.",
    "string_too_long": "Debe tener como maximo {max_length} caracteres.",
    "string_type": "Debe ser un texto.",
    "float_type": "Debe ser un numero.",
    "float_parsing": "Debe ser un numero.",
    "int_type": "Debe ser un numero entero.",
    "int_parsing": "Debe ser un numero entero.",
    "bool_type": "Debe ser verdadero o falso.",
    "greater_than_equal": "Debe ser mayor o igual a {ge}.",
    "less_than_equal": "Debe ser menor o igual a {le}.",
    "dict_type": "Debe ser un objeto.",
    "model_type": "Debe ser un objeto.",
    "json_invalid": "El cuerpo no es un JSON valido.",
    "literal_error": "Valor no permitido. Opciones: {expected}.",
}


def _validation_message(error: dict[str, Any]) -> str:
    if error["type"] == "value_error" and "error" in error.get("ctx", {}):
        # Messages written by our own validators (e.g. ConsultationRequest.require_inputs).
        return str(error["ctx"]["error"])
    template = _VALIDATION_MESSAGES.get(error["type"])
    if template is None:
        return error["msg"]
    try:
        return template.format(**error.get("ctx", {}))
    except (KeyError, IndexError):
        return error["msg"]


async def _validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    detail = [
        {
            "field": ".".join(str(p) for p in e["loc"] if p != "body") or None,
            "message": _validation_message(e),
        }
        for e in exc.errors()
    ]
    logger.info("%s %s -> invalid_request %s", request.method, request.url.path, detail)
    return error_response(request, ErrorCode.INVALID_REQUEST, detail)


_HTTP_STATUS_CODES = {404: ErrorCode.NOT_FOUND, 405: ErrorCode.METHOD_NOT_ALLOWED}
_DEFAULT_HTTP_DETAILS = {"Not Found", "Method Not Allowed"}


async def _http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code = _HTTP_STATUS_CODES.get(exc.status_code)
    if code is None:
        code = ErrorCode.INTERNAL_ERROR if exc.status_code >= 500 else ErrorCode.INVALID_REQUEST
    detail = None if exc.detail in _DEFAULT_HTTP_DETAILS else exc.detail
    return error_response(request, code, detail, status=exc.status_code, headers=exc.headers)


def _declared_body_too_large(request: Request) -> bool:
    """Rejects bodies whose Content-Length exceeds MAX_REQUEST_BYTES before reading them."""
    length = request.headers.get("content-length")
    return length is not None and length.isdigit() and int(length) > get_settings().max_request_bytes


async def _request_middleware(request: Request, call_next):
    """Wraps EVERY endpoint, current and future.

    - Assigns a request id (the client's X-Request-ID or a new one), exposes it to the logs and
      returns it in the response header. Handlers run inside, so request.state always has it.
    - Rejects oversized bodies (declared Content-Length) with request_too_large.
    - Any unexpected exception is logged with its traceback and answered as internal_error:
      the request fails in a controlled way, without internal details, and the server keeps serving.
    """
    client_id = request.headers.get(REQUEST_ID_HEADER, "")
    request_id = client_id[:_MAX_CLIENT_REQUEST_ID] if client_id.isprintable() and client_id else uuid.uuid4().hex[:12]
    request.state.request_id = request_id
    token = request_id_var.set(request_id)
    started = time.perf_counter()
    try:
        try:
            if _declared_body_too_large(request):
                response = error_response(request, ErrorCode.REQUEST_TOO_LARGE)
            else:
                response = await call_next(request)
        except Exception:
            logger.exception("Unhandled error in %s %s", request.method, request.url.path)
            response = error_response(request, ErrorCode.INTERNAL_ERROR)
        response.headers[REQUEST_ID_HEADER] = request_id
        logger.info(
            "%s %s %s %.0fms",
            request.method,
            request.url.path,
            response.status_code,
            (time.perf_counter() - started) * 1000,
        )
        return response
    finally:
        request_id_var.reset(token)


def register_error_handling(app: FastAPI) -> None:
    """Call before adding CORS, so CORS stays outermost and error responses also get its headers."""
    app.middleware("http")(_request_middleware)
    app.add_exception_handler(AppError, _app_error_handler)
    app.add_exception_handler(RequestValidationError, _validation_handler)
    app.add_exception_handler(StarletteHTTPException, _http_exception_handler)


# Documents the error contract in OpenAPI for every v1 route.
RATE_LIMITED_RESPONSES: dict[int | str, dict[str, Any]] = {
    429: {"model": ErrorResponse, "description": "Rate limit exceeded (see Retry-After)"},
}

ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    status: {"model": ErrorResponse, "description": description}
    for status, description in {
        422: "Invalid input",
        500: "Internal error",
    }.items()
}
