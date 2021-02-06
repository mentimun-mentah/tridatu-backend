from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi_jwt_auth import AuthJWT
from controllers.UserController import UserFetch, UserCrud
from controllers.ConfirmationController import ConfirmationCrud
from config import settings, oauth

router = APIRouter()

@router.get('/google',status_code=302,response_class=RedirectResponse,
    responses={
        302: {"description": "Redirect to google login services"}
    }
)
async def google_login(request: Request):
    return await oauth.google.authorize_redirect(request, settings.GOOGLE_REDIRECT_URI)

@router.get('/google/authorized',status_code=307,response_class=RedirectResponse,
    responses={
        307: {"description":"Redirect to frontend app"}
    }
)
async def google_authorize(request: Request, authorize: AuthJWT = Depends()):
    token = await oauth.google.authorize_access_token(request)
    user_data = await oauth.google.parse_id_token(request, token)
    user_data = dict(user_data)

    access_expires = None
    user = await UserFetch.filter_by_email(user_data['email'])
    if not user:
        # save user to database
        user_id = await UserCrud.save_user_from_oauth(
            username=user_data['name'],
            email=user_data['email'],
            avatar=user_data['picture']
        )
        await ConfirmationCrud.create_confirmation_activated(user_id)
    else:
        user_id = user['id']
        access_expires = None if user['role'] != 'admin' else settings.access_expires_admin

    # set token and redirect to frontend app
    access_token = authorize.create_access_token(subject=user_id,expires_time=access_expires)
    refresh_token = authorize.create_refresh_token(subject=user_id)

    response = RedirectResponse(settings.frontend_uri)
    authorize.set_access_cookies(access_token,response)
    authorize.set_refresh_cookies(refresh_token,response)
    return response

@router.get('/facebook',status_code=302,response_class=RedirectResponse,
    responses={
        302: {"description": "Redirect to facebook login services"}
    }
)
async def facebook_login(request: Request):
    return await oauth.facebook.authorize_redirect(request, settings.FACEBOOK_REDIRECT_URI)

@router.get('/facebook/authorized',status_code=307,response_class=RedirectResponse,
    responses={
        307: {"description":"Redirect to frontend app"}
    }
)
async def facebook_authorize(request: Request, authorize: AuthJWT = Depends()):
    token = await oauth.facebook.authorize_access_token(request)
    user_data = await oauth.facebook.get('me?fields=name,email,picture',token=token)
    user_data = user_data.json()

    access_expires = None
    user = await UserFetch.filter_by_email(user_data['email'])
    if not user:
        # save user to database
        user_id = await UserCrud.save_user_from_oauth(
            username=user_data['name'],
            email=user_data['email'],
            avatar=user_data['picture']['data']['url']
        )
        await ConfirmationCrud.create_confirmation_activated(user_id)
    else:
        user_id = user['id']
        access_expires = None if user['role'] != 'admin' else settings.access_expires_admin

    # set token and redirect to frontend app
    access_token = authorize.create_access_token(subject=user_id,expires_time=access_expires)
    refresh_token = authorize.create_refresh_token(subject=user_id)

    response = RedirectResponse(settings.frontend_uri)
    authorize.set_access_cookies(access_token,response)
    authorize.set_refresh_cookies(refresh_token,response)
    return response
