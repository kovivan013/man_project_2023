import uvicorn
from fastapi import FastAPI

from routers import api_router
from config import settings


def get_application():
    application = FastAPI()
    application.include_router(api_router)

    return application


app = get_application()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True
    )
