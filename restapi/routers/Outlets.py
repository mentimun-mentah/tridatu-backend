from fastapi import APIRouter, Depends, UploadFile, Path, HTTPException
from fastapi_jwt_auth import AuthJWT
from controllers.OutletController import OutletCrud, OutletFetch
from controllers.UserController import UserFetch
from schemas.outlets.OutletSchema import OutletSchema
from libs.MagicImage import MagicImage, SingleImageRequired
from localization import LocalizationRoute
from I18N import ResponseMessages, HttpError
from config import settings
from typing import List

router = APIRouter(route_class=LocalizationRoute)
# default language response
lang = settings.default_language_code

# dependencies injection for validation an image
single_image_required = SingleImageRequired(
    max_file_size=4,
    allow_file_ext=['jpg','png','jpeg']
)

@router.post('/create',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['create_outlet'][201]}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        413: {
            "description": "Request Entity Too Large",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['single_image.not_lt']['message']}}}
        }
    }
)
async def create_outlet(file: UploadFile = Depends(single_image_required), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    magic_image = MagicImage(file=file.file,width=200,height=200,path_upload='outlets/',square=True)
    magic_image.save_image()

    await OutletCrud.create_outlet(magic_image.file_name)
    return ResponseMessages[lang]['create_outlet'][201]

@router.get('/all-outlets',response_model=List[OutletSchema])
async def get_all_outlets():
    return await OutletFetch.get_all_outlets()

@router.delete('/delete/{outlet_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json": {"example": ResponseMessages[lang]['delete_outlet'][200]}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Outlet not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['outlets.not_found']['message']}}}
        }
    }
)
async def delete_outlet(outlet_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if outlet := await OutletFetch.filter_by_id(outlet_id):
        MagicImage.delete_image(file=outlet['image'],path_delete='outlets/')
        await OutletCrud.delete_outlet(outlet['id'])
        return ResponseMessages[lang]['delete_outlet'][200]
    raise HTTPException(status_code=404,detail=HttpError[lang]['outlets.not_found'])
