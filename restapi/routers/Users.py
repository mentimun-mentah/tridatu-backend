from fastapi import (
    APIRouter,
    Depends,
    Request,
    UploadFile,
    BackgroundTasks,
    HTTPException,
)
from fastapi.responses import RedirectResponse
from fastapi_jwt_auth import AuthJWT
from controllers.UserController import UserCrud, UserFetch, UserLogic
from controllers.ConfirmationController import ConfirmationCrud, ConfirmationFetch, ConfirmationLogic
from controllers.PasswordResetController import PasswordResetFetch, PasswordResetCrud, PasswordResetLogic
from schemas.users.UserSchema import UserRegister, UserEmail, UserLogin, UserResetPassword
from schemas.users.UserPasswordSchema import UserAddPassword, UserUpdatePassword
from libs.MagicImage import MagicImage, SingleImageRequired
from libs.MailSmtp import send_email
from config import settings

router = APIRouter()

# dependencies injection for validation an image
single_image_required = SingleImageRequired(
    max_file_size=4,
    allow_file_ext=['jpg','png','jpeg']
)

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
async def register(request: Request, user: UserRegister, background_tasks: BackgroundTasks):
    if await UserFetch.filter_by_email(user.email):
        raise HTTPException(status_code=400,detail="The email has already been taken.")

    user_id = await UserCrud.create_user(**user.dict(exclude={'confirm_password'}))
    confirm_id = await ConfirmationCrud.create_confirmation(user_id)

    # Send email confirm to user
    email_content = {"link": request.url_for("user_confirm",token=confirm_id), "username": user.username}
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
async def resend_email(request: Request, user: UserEmail, background_tasks: BackgroundTasks):
    # email not found
    if user := await UserFetch.filter_by_email(user.email):
        confirm = await ConfirmationFetch.filter_by_user_id(user['id'])
        # account already activated
        if confirm['activated']:
            raise HTTPException(status_code=400,detail="Your account already activated.")

        # send email confirm
        if confirm['resend_expired'] is None or ConfirmationLogic.resend_is_expired(confirm['resend_expired']):
            # Send email confirm to user
            email_content = {"link": request.url_for("user_confirm",token=confirm['id']), "username": user['username']}
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

@router.post('/password-reset/send',
    responses={
        200: {
            "description":"Successful Response",
            "content": {"application/json":{"example": {"detail":"We have sent a password reset link to your email."}}}
        },
        400: {
            "description": "Account not yet activate or Cooldown time send an email",
            "content": {"application/json":{"example": {"detail":"string"}}}
        },
        404: {
            "description": "Email address not found",
            "content": {"application/json":{"example": {"detail":"We can't find a user with that e-mail address."}}}
        }
    }
)
async def password_reset_send(user: UserEmail, background_tasks: BackgroundTasks):
    if user := await UserFetch.filter_by_email(user.email):
        confirm = await ConfirmationFetch.filter_by_user_id(user['id'])
        if not confirm['activated']:
            raise HTTPException(status_code=400,detail="Please activate your account first.")

        password_reset = await PasswordResetFetch.filter_by_email(user['email'])
        if password_reset is None or PasswordResetLogic.resend_is_expired(password_reset['resend_expired']):
            # add to database if password reset None
            if password_reset is None:
                reset_id = await PasswordResetCrud.create_password_reset(user['email'])
            else:
                reset_id = password_reset['id']
                # increase expired time to 5 minute
                await PasswordResetCrud.change_resend_expired(reset_id)

            # send email reset password to user
            email_content = {"link": settings.frontend_uri + router.url_path_for("password_reset",token=reset_id)}
            background_tasks.add_task(send_email,
                [user['email']],
                'Reset Password',
                'dont-reply',
                'email/EmailResetPassword.html',
                **email_content
            )
            return {"detail": "We have sent a password reset link to your email."}
        # try 5 minute laters
        raise HTTPException(status_code=400,detail="You can try 5 minute later.")
    raise HTTPException(status_code=404,detail="We can't find a user with that e-mail address.")

@router.put('/password-reset/{token}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json": {"example": {"detail":"Successfully reset your password."}}}
        },
        400: {
            "description": "Email password reset not same as input user",
            "content": {"application/json": {"example": {"detail":"The password reset token is invalid."}}}
        },
        404: {
            "description": "Token or Email address not found",
            "content": {"application/json": {"example": {"detail":"string"}}}
        }
    }
)
async def password_reset(token: str, user_data: UserResetPassword):
    if user := await UserFetch.filter_by_email(user_data.email):
        password_reset = await PasswordResetFetch.filter_by_id(token)
        if not password_reset:
            raise HTTPException(status_code=404,detail="Token not found!")

        if not PasswordResetLogic.password_reset_email_same_as_db(user['email'],password_reset['email']):
            raise HTTPException(status_code=400,detail="The password reset token is invalid.")

        await UserCrud.update_password_user(user['id'],user_data.password)  # update password
        await PasswordResetCrud.delete_password_reset(token)  # delete password reset in db

        return {"detail": "Successfully reset your password."}
    raise HTTPException(status_code=404,detail="We can't find a user with that e-mail address.")

@router.post('/add-password',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json": {"example": {"detail":"Success add a password to your account."}}}
        },
        400: {
            "description": "Account already has a password",
            "content": {"application/json": {"example": {"detail":"Your account already has a password."}}}
        }
    }
)
async def add_password(user_data: UserAddPassword, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    if user := await UserFetch.filter_by_id(user_id):
        if user['password']:
            raise HTTPException(status_code=400,detail="Your account already has a password.")

        await UserCrud.update_password_user(user['id'],user_data.password)  # add password
        return {"detail": "Success add a password to your account."}

@router.put('/update-password',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json": {"example": {"detail":"Success update your password."}}}
        },
        400: {
            "description": "Password not found in database",
            "content": {"application/json": {"example": {"detail":"Please add your password first."}}}
        }
    }
)
async def update_password(user_data: UserUpdatePassword, authorize: AuthJWT = Depends()):
    authorize.fresh_jwt_required()

    user_id = authorize.get_jwt_subject()
    if user := await UserFetch.filter_by_id(user_id):
        if not user['password']:
            raise HTTPException(status_code=400,detail="Please add your password first.")

        if not UserLogic.password_is_same_as_hash(user_data.old_password,user['password']):
            raise HTTPException(status_code=422,detail="Password does not match with our records.")

        await UserCrud.update_password_user(user['id'],user_data.password)  # update password
        return {"detail": "Success update your password."}

@router.put('/update-avatar',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json": {"example": {"detail":"The image profile has updated."}}}
        },
        413: {
            "description": "Request Entity Too Large",
            "content": {"application/json": {"example": {"detail":"An image cannot greater than 4 Mb."}}}
        }
    }
)
async def update_avatar(file: UploadFile = Depends(single_image_required), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    if user := await UserFetch.filter_by_id(user_id):
        # if user avatar not same as default, delete the old one
        if user['avatar'] != 'default.jpg':
            MagicImage.delete_image(file=user['avatar'],path_delete='avatars/')

        magic_image = MagicImage(file=file.file,width=260,height=260,path_upload='avatars/',square=True)
        magic_image.save_image()

        await UserCrud.update_avatar_user(user['id'],magic_image.file_name)
        return {"detail": "The image profile has updated."}
