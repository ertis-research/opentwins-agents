from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from routes.agents import BaseRouter


__name__ = "OpenTwins FMI simulator 2.0"
__name__ = "0.1.0"

app = FastAPI()
app.include_router(BaseRouter)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="OpenTwins Agents",
        version="0.1.0",
        description="This is the OpenTwins Agent API",
        routes=app.routes,
    )
    openapi_schema["servers"] = [
        {"url": "/", "description": "Default"},
        {"url": "https//localhost:8001", "description": "Localhost"}
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi