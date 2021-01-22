import inspect, re
from fastapi import FastAPI, Request
from fastapi.routing import APIRoute
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.middleware.sessions import SessionMiddleware
from config import database, redis_conn, settings
from routers import (
    Users, OAuth2, Address, Outlets,
    Brands, Categories, SubCategories, ItemSubCategories,
    Products, Variants, Wishlists, Shipping,
    Comments, Replies, WholeSale
)

app = FastAPI(default_response_class=ORJSONResponse,docs_url=None,redoc_url=None)

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

@app.get("/docs",include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Tridatu Bali ID",
        swagger_css_url="/static/swagger-ui.css",
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
    openapi_schema["components"].update({
        "securitySchemes": {
            "AuthJWTCookieAccess": {
                "type": "apiKey",
                "in": "header",
                "name": "X-CSRF-TOKEN"
            },
            "AuthJWTCookieRefresh": {
                "type": "apiKey",
                "in": "header",
                "name": "X-CSRF-TOKEN"
            }
        }
    })
    refresh_token_cookie = {
        "name": "refresh_token_cookie",
        "in": "cookie",
        "required": False,
        "schema": {
            "title": "refresh_token_cookie",
            "type": "string"
        }
    }
    access_token_cookie = {
        "name": "access_token_cookie",
        "in": "cookie",
        "required": False,
        "schema": {
            "title": "access_token_cookie",
            "type": "string"
        }
    }

    api_router = [route for route in app.routes if isinstance(route, APIRoute)]

    for route in api_router:
        path = getattr(route, "path")
        endpoint = getattr(route,"endpoint")
        methods = [method.lower() for method in getattr(route, "methods")]

        for method in methods:
            # access_token
            if (
                re.search("jwt_required",inspect.getsource(endpoint)) or
                re.search("fresh_jwt_required",inspect.getsource(endpoint)) or
                re.search("jwt_optional",inspect.getsource(endpoint))
            ):
                try:
                    openapi_schema["paths"][path][method]['parameters'].append(access_token_cookie)
                except Exception:
                    openapi_schema["paths"][path][method].update({"parameters":[access_token_cookie]})

                # method GET doesn't need to pass X-CSRF-TOKEN
                if method != "get":
                    openapi_schema["paths"][path][method].update({
                        'security': [{"AuthJWTCookieAccess": []}]
                    })

            # refresh_token
            if re.search("jwt_refresh_token_required",inspect.getsource(endpoint)):
                try:
                    openapi_schema["paths"][path][method]['parameters'].append(refresh_token_cookie)
                except Exception:
                    openapi_schema["paths"][path][method].update({"parameters":[refresh_token_cookie]})

                # method GET doesn't need to pass X-CSRF-TOKEN
                if method != "get":
                    openapi_schema["paths"][path][method].update({
                        'security': [{"AuthJWTCookieRefresh": []}]
                    })

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.include_router(Users.router,tags=['users'],prefix="/users")
app.include_router(OAuth2.router,tags=['oauth'],prefix="/login")
app.include_router(Address.router,tags=['address'],prefix="/address")
app.include_router(Outlets.router,tags=['outlets'],prefix="/outlets")
app.include_router(Brands.router,tags=['brands'],prefix="/brands")
app.include_router(Categories.router,tags=['categories'],prefix="/categories")
app.include_router(SubCategories.router,tags=['sub-categories'],prefix="/sub-categories")
app.include_router(ItemSubCategories.router,tags=['item-sub-categories'],prefix="/item-sub-categories")
app.include_router(Products.router,tags=['products'],prefix="/products")
app.include_router(Variants.router,tags=['variants'],prefix="/variants")
app.include_router(WholeSale.router,tags=['wholesale'],prefix="/wholesale")
app.include_router(Wishlists.router,tags=['wishlists'],prefix="/wishlists")
app.include_router(Shipping.router,tags=['shipping'],prefix="/shipping")
app.include_router(Comments.router,tags=['comments'],prefix="/comments")
app.include_router(Replies.router,tags=['replies'],prefix="/replies")
