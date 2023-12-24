from fastapi import FastAPI

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from man_project_2023.utils.schemas.schemas import DataStructure
from man_project_2023.utils.debug import exceptions

class Reporter:

    @staticmethod
    def api_reporter(app: FastAPI):

        async def wrapper(exception: HTTPException):
            result = DataStructure()
            result._status = exception.status_code
            result.message = exception.detail

            return JSONResponse(status_code=result.status,
                                content=result.model_dump())

        @app.exception_handler(RequestValidationError)
        async def _422_wrapper(request, exc):
            return await wrapper(exceptions.InvalidInputData)

    @staticmethod
    def api_exception(exception: HTTPException):
        result = DataStructure()
        result._status = exception.status_code
        result.message = exception.detail

        return result
