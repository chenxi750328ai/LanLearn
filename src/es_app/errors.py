from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from es_app.schemas.common import ErrorBody


class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details=None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_req: Request, exc: AppError):
        body = ErrorBody(code=exc.code, message=exc.message, details=exc.details)
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())
