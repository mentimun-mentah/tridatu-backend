from fastapi import (
    APIRouter,
    Depends,
    Request,
    BackgroundTasks,
    HTTPException,
)
from fastapi.responses import RedirectResponse
from fastapi_jwt_auth import AuthJWT
from controllers.UserController import UserCrud, UserFetch
from controllers.ConfirmationController import ConfirmationCrud, ConfirmationFetch
from schemas.users.RegisterSchema import RegisterSchema
from libs.MailSmtp import send_email
from config import settings

router = APIRouter()

@router.post('/register',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Check your email to activated user."}}}
        }
    }
)
async def register(request: Request, user: RegisterSchema, background_tasks: BackgroundTasks):
    if await UserFetch.filter_by_email(user.email):
        raise HTTPException(status_code=422,detail="The email has already been taken.")

    user_id = await UserCrud.create_user(**user.dict(exclude={'confirm_password'}))
    confirm_id = await ConfirmationCrud.create_confirmation(user_id)

    email_content = {"link": request.url_for("user_confirm",token=confirm_id), "username": user.username}
    # Send email confirm to user
    background_tasks.add_task(send_email,
        [user.email],
        'Activated User',
        'dont-reply',
        'email/EmailConfirm.html',
        **email_content
    )

    return {"detail":"Check your email to activated user."}

@router.get('/user-confirm/{token}',status_code=307,response_class=RedirectResponse)
async def user_confirm(token: str, authorize: AuthJWT = Depends()):
    if (confirmation := await ConfirmationFetch.filter_by_id(token)):
        if not confirmation['activated']:
            await ConfirmationCrud.user_activated(token)

        access_token = authorize.create_access_token(subject=confirmation['user_id'],fresh=True)
        refresh_token = authorize.create_refresh_token(subject=confirmation['user_id'])
        # set jwt in cookies
        response = RedirectResponse(settings.frontend_uri)
        authorize.set_access_cookies(access_token,response)
        authorize.set_refresh_cookies(refresh_token,response)
        return response
    raise HTTPException(status_code=404,detail="Token not found!")
