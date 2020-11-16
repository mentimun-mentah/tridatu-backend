from fastapi import FastAPI, Request
from fastapi.routing import APIRoute
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.middleware.sessions import SessionMiddleware
from config import database, redis_conn, settings
from docs import (
    refresh_token_cookie,
    access_token_cookie,
    csrf_token_header,
    list_refresh_token,
    list_access_token,
    list_access_token_without_csrf
)
from routers import Users, OAuth2, Address

app = FastAPI(default_response_class=ORJSONResponse)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(SessionMiddleware, secret_key=settings.authjwt_secret_key)
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

    api_router = [route for route in app.routes if isinstance(route, APIRoute)]

    for route in api_router:
        method = list(route.methods)[0].lower()
        try:
            if route.name in list_refresh_token:
                openapi_schema["paths"][route.path][method]['parameters'].append(refresh_token_cookie)
                openapi_schema["paths"][route.path][method]['parameters'].append(csrf_token_header)
            if route.name in list_access_token:
                openapi_schema["paths"][route.path][method]['parameters'].append(access_token_cookie)
                openapi_schema["paths"][route.path][method]['parameters'].append(csrf_token_header)
            if route.name in list_access_token_without_csrf:
                openapi_schema["paths"][route.path][method]['parameters'].append(access_token_cookie)
        except Exception:
            if route.name in list_refresh_token:
                openapi_schema["paths"][route.path][method].update({"parameters":[refresh_token_cookie]})
                openapi_schema["paths"][route.path][method]['parameters'].append(csrf_token_header)
            if route.name in list_access_token:
                openapi_schema["paths"][route.path][method].update({"parameters":[access_token_cookie]})
                openapi_schema["paths"][route.path][method]['parameters'].append(csrf_token_header)
            if route.name in list_access_token_without_csrf:
                openapi_schema["paths"][route.path][method].update({"parameters":[access_token_cookie]})

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.include_router(Users.router,tags=['users'],prefix="/users")
app.include_router(OAuth2.router,tags=['oauth'],prefix="/login")
app.include_router(Address.router,tags=['address'],prefix="/address")
