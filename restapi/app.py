from fastapi import FastAPI, Request
from fastapi.routing import APIRoute
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth.exceptions import AuthJWTException
from config import database, redis_conn, settings
from routers import Users

app = FastAPI(default_response_class=ORJSONResponse)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_uri],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    app.state.redis = redis_conn
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

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

    refresh_token_cookie = {
        "name": "refresh_token_cookie",
        "in": "cookie",
        "required": False,
        "schema": {
            "title": "refresh_token_cookie",
            "type": "string"
        }
    }

    refresh_csrf_header = {
        "name": "X-CSRF-TOKEN",
        "in": "header",
        "required": True,
        "schema": {
            "title": "X-CSRF-TOKEN",
            "type": "string"
        }
    }

    api_router = [route for route in app.routes if isinstance(route, APIRoute)]

    for route in api_router:
        method = list(route.methods)[0].lower()
        try:
            if route.operation_id == "authorize_refresh_token":
                openapi_schema["paths"][route.path][method]['parameters'].append(refresh_token_cookie)
                openapi_schema["paths"][route.path][method]['parameters'].append(refresh_csrf_header)
        except Exception:
            if route.operation_id == "authorize_refresh_token":
                openapi_schema["paths"][route.path][method].update({"parameters":[refresh_token_cookie]})
                openapi_schema["paths"][route.path][method]['parameters'].append(refresh_csrf_header)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.include_router(Users.router,tags=['users'],prefix="/users")
