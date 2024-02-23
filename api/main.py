import uvicorn
import os
from fastapi import FastAPI

from services.errors_reporter import Reporter

from routers import api_router
from config import settings


def get_application():
    application = FastAPI()
    application.include_router(api_router)

    return application


app = get_application()

Reporter.api_reporter(app)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True
    )
