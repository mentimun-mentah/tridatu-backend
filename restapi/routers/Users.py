from fastapi import (
    APIRouter,
    Depends,
    Request,
    BackgroundTasks,
    HTTPException,
)
from fastapi.responses import RedirectResponse
from fastapi_jwt_auth import AuthJWT
from controllers.UserController import UserCrud, UserFetch, UserLogic
from controllers.ConfirmationController import ConfirmationCrud, ConfirmationFetch, ConfirmationLogic
from schemas.users.RegisterSchema import RegisterSchema
from schemas.users.UserSchema import UserResendEmail, UserLogin
from libs.MailSmtp import send_email
from config import settings

router = APIRouter()

@router.post('/register',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Check your email to activated user."}}}
        },
        400: {
            "description": "Email already taken",
            "content": {"application/json":{"example": {"detail":"The email has already been taken."}}}
        }
    }
)
async def register(request: Request, user: RegisterSchema, background_tasks: BackgroundTasks):
    if await UserFetch.filter_by_email(user.email):
        raise HTTPException(status_code=400,detail="The email has already been taken.")

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

@router.get('/user-confirm/{token}',status_code=307,response_class=RedirectResponse,
    responses={
        307: {"description":"Redirect to frontend app"},
        404: {
            "description": "Token not found",
            "content": {"application/json": {"example": {"detail": "Token not found!"}}}
        }
    }
)
async def user_confirm(token: str, authorize: AuthJWT = Depends()):
    if confirmation := await ConfirmationFetch.filter_by_id(token):
        if not confirmation['activated']:
            await ConfirmationCrud.user_activated(token)

        access_token = authorize.create_access_token(subject=confirmation['user_id'])
        refresh_token = authorize.create_refresh_token(subject=confirmation['user_id'])
        # set jwt in cookies
        response = RedirectResponse(settings.frontend_uri)
        authorize.set_access_cookies(access_token,response)
        authorize.set_refresh_cookies(refresh_token,response)
        return response
    raise HTTPException(status_code=404,detail="Token not found!")

@router.post('/resend-email',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json": {"example": {"detail":"Email confirmation has send."}}}
        },
        400: {
            "description": "Account already activated or Cooldown time send an email",
            "content": {"application/json": {"example": {"detail": "string"}}}
        },
        404: {
            "description": "Email not found",
            "content": {"application/json": {"example": {"detail": "Email not found."}}}
        }
    }
)
async def resend_email(request: Request, user: UserResendEmail, background_tasks: BackgroundTasks):
    # email not found
    if user := await UserFetch.filter_by_email(user.email):
        confirm = await ConfirmationFetch.filter_by_user_id(user['id'])
        # account already activated
        if confirm['activated']:
            raise HTTPException(status_code=400,detail="Your account already activated.")

        # send email confirm
        if confirm['resend_expired'] is None or ConfirmationLogic.resend_is_expired(confirm['resend_expired']):
            email_content = {"link": request.url_for("user_confirm",token=confirm['id']), "username": user['username']}
            # Send email confirm to user
            background_tasks.add_task(send_email,
                [user['email']],
                'Activated User',
                'dont-reply',
                'email/EmailConfirm.html',
                **email_content
            )
            # generate resend expired
            await ConfirmationLogic.generate_resend_expired(confirm['id'])

            return {"detail":"Email confirmation has send."}
        # try 5 minute laters
        raise HTTPException(status_code=400,detail="You can try 5 minute later.")
    raise HTTPException(status_code=404,detail="Email not found.")

@router.post('/login',
    responses={
        200: {
            "description":"Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully login."}}}
        },
        400: {
            "description":"Account not yet activate",
            "content": {"application/json":{"example": {"detail":"Please check your email to activate your account."}}}
        }
    }
)
async def login(user_data: UserLogin, authorize: AuthJWT = Depends()):
    if user := await UserFetch.filter_by_email(user_data.email):
        if user['password'] and UserLogic.password_is_same_as_hash(user_data.password,user['password']):
            confirm = await ConfirmationFetch.filter_by_user_id(user['id'])
            if confirm['activated']:
                access_token = authorize.create_access_token(subject=user['id'],fresh=True)
                refresh_token = authorize.create_refresh_token(subject=user['id'])
                # set jwt in cookies
                authorize.set_access_cookies(access_token)
                authorize.set_refresh_cookies(refresh_token)
                return {"detail":"Successfully login."}
            raise HTTPException(status_code=400,detail="Please check your email to activate your account.")
        raise HTTPException(status_code=422,detail="Invalid credential.")
    raise HTTPException(status_code=422,detail="Invalid credential.")

@router.post('/refresh-token',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"The token has been refreshed."}}}
        }
    }
)
def refresh_token(authorize: AuthJWT = Depends()):
    authorize.jwt_refresh_token_required()

    user_id = authorize.get_jwt_subject()
    new_token = authorize.create_access_token(subject=user_id)
    authorize.set_access_cookies(new_token)
    return {"detail": "The token has been refreshed."}

@router.delete('/access-revoke',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"An access token has revoked."}}}
        }
    }
)
def access_revoke(request: Request, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    jti = authorize.get_raw_jwt()['jti']
    request.app.state.redis.set(jti,'true',settings.access_expires)
    return {"detail": "An access token has revoked."}

@router.delete('/refresh-revoke',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"An refresh token has revoked."}}}
        }
    }
)
def refresh_revoke(request: Request, authorize: AuthJWT = Depends()):
    authorize.jwt_refresh_token_required()

    jti = authorize.get_raw_jwt()['jti']
    request.app.state.redis.set(jti,'true',settings.refresh_expires)
    return {"detail": "An refresh token has revoked."}
