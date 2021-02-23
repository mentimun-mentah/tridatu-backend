from fastapi import Request, Response
from fastapi.routing import APIRoute
from fastapi.responses import ORJSONResponse
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler
)
from I18N import (
    PydanticError,
    ResponseMessages,
    HttpError
)
from typing import Callable, Any

class SystemLocalizationMiddleware:
    """
    Middleware to get Accept-Language and save to request.state.
    """
    def __init__(self, default_language_code: str) -> None:
        self.default_language_code = default_language_code

    async def __call__(self, request: Request, call_next):
        language_code = request.headers.get('accept-language') or self.default_language_code

        language_code = language_code.split(',')[0]
        # set language_code from doc to default
        if language_code == 'en-US':
            language_code = self.default_language_code

        if language_code not in ['id','en']:
            return ORJSONResponse(
                status_code=422,
                content={"detail": "The languages available were id and en."}
            )

        # set language_code to state
        request.state.language_code = language_code

        response = await call_next(request)
        return response

class TranslateORJSONResponse(ORJSONResponse):
    """
    Response that localization content
    """
    def __init__(self, content: Any = None, *args, **kwargs):
        self.original_content = content
        super().__init__(content, *args, **kwargs)

    def translate_content(self, language_code: str, endpoint: str):
        content = self.original_content

        self.headers.__delitem__('content-length')
        self.headers.__delitem__('content-type')

        if msg := ResponseMessages[language_code].get(endpoint):
            content = msg.get(self.status_code)

        return TranslateORJSONResponse(
            content, status_code=self.status_code,
            headers=self.headers, background=self.background
        )

class LocalizationRoute(APIRoute):
    """
    Route that localization response
    """
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            response: Response = await original_route_handler(request)

            if isinstance(response, TranslateORJSONResponse):
                return response.translate_content(
                    request.state.language_code,
                    request.__getitem__('endpoint').__name__
                )
            return response
        return custom_route_handler

async def request_validation_exception_handler_translate(request, exc):
    """
    Validation exception handler with localization
    """
    language_code = request.state.language_code

    for error in exc.errors():
        msg = PydanticError[language_code].get(error['type']) or error['msg']
        if ctx := error.get('ctx'):
            if error['type'] == 'value_error.const':
                ctx.update({'permitted': ', '.join(repr(v) for v in ctx['permitted'])})
            if error['type'] == 'type_error.enum':
                ctx.update({'permitted': ', '.join(repr(v.value) for v in ctx['enum_values'])})
            msg = msg.format(**ctx)
        error['msg'] = msg

    return await request_validation_exception_handler(request, exc)

async def http_exception_handler_translate(request, exc):
    """
    Http exception handler with localization
    """
    language_code = request.state.language_code

    # check if detail is dictionary or not
    if isinstance(exc.detail, dict):
        if error := HttpError[language_code].get(exc.detail.get('code')):
            exc.detail = error['message']

    return await http_exception_handler(request, exc)
