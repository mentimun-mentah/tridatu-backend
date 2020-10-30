from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from config import database
from routers import Users

app = FastAPI(default_response_class=ORJSONResponse)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Tridatu Bali ID",
        version="1.0.0",
        description="Documentation Tridatu Bali ID",
        routes=app.routes
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://bit.ly/2HKSAjU"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.include_router(Users.router,tags=['users'])
