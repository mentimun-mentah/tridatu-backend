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
from schemas.users.UserSchema import UserRegister, UserEmail, UserLogin, UserResetPassword, UserData
from schemas.users.UserPasswordSchema import UserAddPassword, UserUpdatePassword, UserConfirmPassword
from schemas.users.UserAccountSchema import UserAccountSchema
from libs.MagicImage import MagicImage, SingleImageRequired
from libs.MailSmtp import send_email
from localization import LocalizationRoute
from I18N import ResponseMessages, HttpError
from config import settings

router = APIRouter(route_class=LocalizationRoute)
# default language response
lang = settings.default_language_code

# dependencies injection for validation an image
single_image_required = SingleImageRequired(
    max_file_size=4,
    allow_file_ext=['jpg','png','jpeg']
)

@router.post('/register',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['register'][201]}}
        },
        400: {
            "description": "Email already taken",
            "content": {"application/json":{"example": {"detail": HttpError[lang]['users.email_taken']['message']}}}
        }
    }
)
async def register(request: Request, user: UserRegister, background_tasks: BackgroundTasks):
    if await UserFetch.filter_by_email(user.email):
        raise HTTPException(status_code=400,detail=HttpError[lang]['users.email_taken'])

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

    return ResponseMessages[lang]['register'][201]

@router.get('/user-confirm/{token}',status_code=307,response_class=RedirectResponse,
    responses={
        307: {"description":"Redirect to frontend app"},
        404: {
            "description": "Token not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['users.token_not_found']['message']}}}
        }
    }
)
async def user_confirm(token: str, authorize: AuthJWT = Depends()):
    if confirmation := await ConfirmationFetch.filter_by_id(token):
        if not confirmation['activated']:
            await ConfirmationCrud.user_activated(token)

        access_token = authorize.create_access_token(subject=str(confirmation['user_id']),fresh=True)
        refresh_token = authorize.create_refresh_token(subject=str(confirmation['user_id']))
        # set jwt in cookies
        response = RedirectResponse(settings.frontend_uri)
        authorize.set_access_cookies(access_token,response)
        authorize.set_refresh_cookies(refresh_token,response)
        return response
    raise HTTPException(status_code=404,detail=HttpError[lang]['users.token_not_found'])

@router.post('/resend-email',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json": {"example": ResponseMessages[lang]['resend_email'][200]}}
        },
        400: {
            "description": "Account already activated or Cooldown time send an email",
            "content": {"application/json": {"example": {"detail": "string"}}}
        },
        404: {
            "description": "Email not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['users.email_not_found_1']['message']}}}
        }
    }
)
async def resend_email(request: Request, user: UserEmail, background_tasks: BackgroundTasks):
    # email not found
    if user := await UserFetch.filter_by_email(user.email):
        confirm = await ConfirmationFetch.filter_by_user_id(user['id'])
        # account already activated
        if confirm['activated']:
            raise HTTPException(status_code=400,detail=HttpError[lang]['users.already_activated'])

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

            return ResponseMessages[lang]['resend_email'][200]
        # try 5 minute laters
        raise HTTPException(status_code=400,detail=HttpError[lang]['users.email_cooldown'])
    raise HTTPException(status_code=404,detail=HttpError[lang]['users.email_not_found_1'])

@router.post('/login',
    responses={
        200: {
            "description":"Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['login'][200]}}
        },
        400: {
            "description":"Account not yet activate",
            "content": {"application/json":{"example": {"detail": HttpError[lang]['users.not_activated_email']['message']}}}
        }
    }
)
async def login(user_data: UserLogin, authorize: AuthJWT = Depends()):
    if user := await UserFetch.filter_by_email(user_data.email):
        if user['password'] and UserLogic.password_is_same_as_hash(user_data.password,user['password']):
            confirm = await ConfirmationFetch.filter_by_user_id(user['id'])
            if confirm['activated']:
                access_expires = None if user['role'] != 'admin' else settings.access_expires_admin

                access_token = authorize.create_access_token(subject=str(user['id']),fresh=True,expires_time=access_expires)
                refresh_token = authorize.create_refresh_token(subject=str(user['id']))
                # set jwt in cookies
                authorize.set_access_cookies(access_token)
                authorize.set_refresh_cookies(refresh_token)
                return ResponseMessages[lang]['login'][200]
            raise HTTPException(status_code=400,detail=HttpError[lang]['users.not_activated_email'])
        raise HTTPException(status_code=422,detail=HttpError[lang]['users.invalid_credential'])
    raise HTTPException(status_code=422,detail=HttpError[lang]['users.invalid_credential'])

@router.post('/fresh-token',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json": {"example": ResponseMessages[lang]['fresh_token'][200]}}
        }
    }
)
async def fresh_token(user_data: UserConfirmPassword, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    if user := await UserFetch.filter_by_id(user_id):
        if not UserLogic.password_is_same_as_hash(user_data.password,user['password']):
            raise HTTPException(status_code=422,detail=HttpError[lang]['users.password_not_match'])

        # set fresh access token in cookie
        access_expires = None if user['role'] != 'admin' else settings.access_expires_admin

        access_token = authorize.create_access_token(subject=str(user['id']),fresh=True,expires_time=access_expires)
        authorize.set_access_cookies(access_token)
        return ResponseMessages[lang]['fresh_token'][200]

@router.post('/refresh-token',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['refresh_token'][200]}}
        }
    }
)
async def refresh_token(authorize: AuthJWT = Depends()):
    authorize.jwt_refresh_token_required()

    user_id = int(authorize.get_jwt_subject())
    if user := await UserFetch.filter_by_id(user_id):
        access_expires = None if user['role'] != 'admin' else settings.access_expires_admin

        new_token = authorize.create_access_token(subject=str(user_id),expires_time=access_expires)
        authorize.set_access_cookies(new_token)
        return ResponseMessages[lang]['refresh_token'][200]

@router.delete('/access-revoke',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['access_revoke'][200]}}
        }
    }
)
def access_revoke(request: Request, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    jti = authorize.get_raw_jwt()['jti']
    request.app.state.redis.set(jti,'true',settings.access_expires)
    return ResponseMessages[lang]['access_revoke'][200]

@router.delete('/refresh-revoke',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['refresh_revoke'][200]}}
        }
    }
)
def refresh_revoke(request: Request, authorize: AuthJWT = Depends()):
    authorize.jwt_refresh_token_required()

    jti = authorize.get_raw_jwt()['jti']
    request.app.state.redis.set(jti,'true',settings.refresh_expires)
    return ResponseMessages[lang]['refresh_revoke'][200]

@router.delete('/delete-cookies',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['delete_cookies'][200]}}
        }
    }
)
def delete_cookies(authorize: AuthJWT = Depends()):
    authorize.unset_jwt_cookies()

    return ResponseMessages[lang]['delete_cookies'][200]

@router.post('/password-reset/send',
    responses={
        200: {
            "description":"Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['password_reset_send'][200]}}
        },
        400: {
            "description": "Account not yet activate or Cooldown time send an email",
            "content": {"application/json":{"example": {"detail":"string"}}}
        },
        404: {
            "description": "Email address not found",
            "content": {"application/json":{"example": {"detail": HttpError[lang]['users.email_not_found_2']['message']}}}
        }
    }
)
async def password_reset_send(user: UserEmail, background_tasks: BackgroundTasks):
    if user := await UserFetch.filter_by_email(user.email):
        confirm = await ConfirmationFetch.filter_by_user_id(user['id'])
        if not confirm['activated']:
            raise HTTPException(status_code=400,detail=HttpError[lang]['users.not_activated'])

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
            return ResponseMessages[lang]['password_reset_send'][200]
        # try 5 minute laters
        raise HTTPException(status_code=400,detail=HttpError[lang]['users.email_cooldown'])
    raise HTTPException(status_code=404,detail=HttpError[lang]['users.email_not_found_2'])

@router.put('/password-reset/{token}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json": {"example": ResponseMessages[lang]['password_reset'][200]}}
        },
        400: {
            "description": "Email password reset not same as input user",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['users.password_reset_invalid']['message']}}}
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
            raise HTTPException(status_code=404,detail=HttpError[lang]['users.token_not_found'])

        if not PasswordResetLogic.password_reset_email_same_as_db(user['email'],password_reset['email']):
            raise HTTPException(status_code=400,detail=HttpError[lang]['users.password_reset_invalid'])

        await UserCrud.update_password_user(user['id'],user_data.password)  # update password
        await PasswordResetCrud.delete_password_reset(token)  # delete password reset in db

        return ResponseMessages[lang]['password_reset'][200]
    raise HTTPException(status_code=404,detail=HttpError[lang]['users.email_not_found_2'])

@router.post('/add-password',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json": {"example": ResponseMessages[lang]['add_password'][201]}}
        },
        400: {
            "description": "Account already has a password",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['users.already_password']['message']}}}
        }
    }
)
async def add_password(user_data: UserAddPassword, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    if user := await UserFetch.filter_by_id(user_id):
        if user['password']:
            raise HTTPException(status_code=400,detail=HttpError[lang]['users.already_password'])

        await UserCrud.update_password_user(user['id'],user_data.password)  # add password
        return ResponseMessages[lang]['add_password'][201]

@router.put('/update-password',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json": {"example": ResponseMessages[lang]['update_password'][200]}}
        },
        400: {
            "description": "Password not found in database",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['users.password_missing']['message']}}}
        }
    }
)
async def update_password(user_data: UserUpdatePassword, authorize: AuthJWT = Depends()):
    authorize.fresh_jwt_required()

    user_id = int(authorize.get_jwt_subject())
    if user := await UserFetch.filter_by_id(user_id):
        if not user['password']:
            raise HTTPException(status_code=400,detail=HttpError[lang]['users.password_missing'])

        if not UserLogic.password_is_same_as_hash(user_data.old_password,user['password']):
            raise HTTPException(status_code=422,detail=HttpError[lang]['users.password_not_match'])

        await UserCrud.update_password_user(user['id'],user_data.password)  # update password
        return ResponseMessages[lang]['update_password'][200]

@router.put('/update-avatar',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json": {"example": ResponseMessages[lang]['update_avatar'][200]}}
        },
        413: {
            "description": "Request Entity Too Large",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['single_image.not_lt']['message']}}}
        }
    }
)
async def update_avatar(file: UploadFile = Depends(single_image_required), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    if user := await UserFetch.filter_by_id(user_id):
        # if user avatar not same as default, delete the old one
        if user['avatar'] != 'default.jpg':
            MagicImage.delete_image(file=user['avatar'],path_delete='avatars/')

        magic_image = MagicImage(file=file.file,width=260,height=260,path_upload='avatars/',square=True)
        magic_image.save_image()

        await UserCrud.update_avatar_user(user['id'],magic_image.file_name)
        return ResponseMessages[lang]['update_avatar'][200]

@router.put('/update-account',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json": {"example": ResponseMessages[lang]['update_account'][200]}}
        },
        400: {
            "description": "Phone number already taken",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['users.phone_taken']['message']}}}
        }
    }
)
async def update_account(user_data: UserAccountSchema, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    if user := await UserFetch.filter_by_id(user_id):
        # check phone number exists
        if user_phone := await UserFetch.filter_by_phone(user_data.phone):
            if user_phone['id'] != user['id']:
                raise HTTPException(status_code=400,detail=HttpError[lang]['users.phone_taken'])

        await UserCrud.update_account_user(user['id'],**user_data.dict())
        return ResponseMessages[lang]['update_account'][200]

@router.get('/my-user', response_model=UserData)
async def my_user(authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    if user := await UserFetch.filter_by_id(user_id):
        user_data = {index:value for index,value in user.items()}
        user_data['password'] = True if user_data['password'] else False
        return user_data
