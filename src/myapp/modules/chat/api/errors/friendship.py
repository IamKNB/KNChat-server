from fastapi import Request, status
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.routing import APIRoute

from myapp.modules.chat.schemas.friendship_api import ErrorEnvelope
from myapp.modules.chat.services import FriendshipServiceError

FRIENDSHIP_HTTP_CODE_MAP = {
    400: "bad_request",
    401: "not_authenticated",
    403: "forbidden",
    404: "not_found",
    409: "conflict",
}

FRIENDSHIP_HTTP_MESSAGE_MAP = {
    400: "bad request",
    401: "not authenticated",
    403: "forbidden",
    404: "not found",
    409: "conflict",
}

FRIENDSHIP_ERROR_RESPONSES = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorEnvelope,
        "description": "Bad request",
    },
    status.HTTP_401_UNAUTHORIZED: {
        "model": ErrorEnvelope,
        "description": "Not authenticated",
    },
    status.HTTP_403_FORBIDDEN: {
        "model": ErrorEnvelope,
        "description": "Forbidden",
    },
    status.HTTP_404_NOT_FOUND: {
        "model": ErrorEnvelope,
        "description": "Not found",
    },
    status.HTTP_409_CONFLICT: {
        "model": ErrorEnvelope,
        "description": "Conflict",
    },
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "model": ErrorEnvelope,
        "description": "Validation error",
    },
}


def _service_error_json(exc: FriendshipServiceError) -> JSONResponse:
    payload = ErrorEnvelope(
        code=exc.code,
        message=exc.message,
        detail=exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=payload.model_dump(),
    )


def _http_error_json(exc: FastAPIHTTPException) -> JSONResponse:
    payload = ErrorEnvelope(
        code=FRIENDSHIP_HTTP_CODE_MAP.get(exc.status_code, "http_error"),
        message=FRIENDSHIP_HTTP_MESSAGE_MAP.get(exc.status_code, "http error"),
        detail=exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=payload.model_dump(),
        headers=exc.headers,
    )


def _validation_error_json(exc: RequestValidationError) -> JSONResponse:
    payload = ErrorEnvelope(
        code="validation_error",
        message="validation error",
        detail=exc.errors(),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=payload.model_dump(),
    )


class FriendshipRoute(APIRoute):
    def get_route_handler(self):
        route_handler = super().get_route_handler()

        async def friendship_route_handler(request: Request) -> Response:
            try:
                return await route_handler(request)
            except FriendshipServiceError as exc:
                return _service_error_json(exc)
            except RequestValidationError as exc:
                return _validation_error_json(exc)
            except FastAPIHTTPException as exc:
                return _http_error_json(exc)

        return friendship_route_handler
