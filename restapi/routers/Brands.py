from fastapi import APIRouter, Depends, UploadFile, Path, Form, HTTPException
from fastapi_jwt_auth import AuthJWT
from controllers.BrandController import BrandCrud, BrandFetch
from controllers.UserController import UserFetch
from schemas.brands.BrandSchema import BrandSchema
from libs.MagicImage import MagicImage, SingleImageRequired, SingleImageOptional
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

single_image_optional = SingleImageOptional(
    max_file_size=4,
    allow_file_ext=['jpg','png','jpeg']
)

@router.post('/create',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['create_brand'][201]}}
        },
        400: {
            "description": "Name already taken",
            "content": {"application/json":{"example": {"detail": HttpError[lang]['brands.name_taken']['message']}}}
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
async def create_brand(
    name: str = Form(...,min_length=2,max_length=100),
    file: UploadFile = Depends(single_image_required),
    authorize: AuthJWT = Depends()
):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if await BrandFetch.filter_by_name(name):
        raise HTTPException(status_code=400,detail=HttpError[lang]['brands.name_taken'])

    magic_image = MagicImage(file=file.file,width=200,height=200,path_upload='brands/',square=True)
    magic_image.save_image()

    await BrandCrud.create_brand(name,magic_image.file_name)
    return ResponseMessages[lang]['create_brand'][201]

@router.get('/all-brands',response_model=List[BrandSchema])
async def get_all_brands():
    return await BrandFetch.get_all_brands()

@router.get('/get-brand/{brand_id}',response_model=BrandSchema,
    responses={
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Brand not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['brands.not_found']['message']}}}
        }
    }
)
async def get_brand_by_id(brand_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if brand := await BrandFetch.filter_by_id(brand_id):
        return {index:value for index,value in brand.items()}
    raise HTTPException(status_code=404,detail=HttpError[lang]['brands.not_found'])

@router.put('/update/{brand_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['update_brand'][200]}}
        },
        400: {
            "description": "Name already taken",
            "content": {"application/json":{"example": {"detail": HttpError[lang]['brands.name_taken']['message']}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Brand not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['brands.not_found']['message']}}}
        },
        413: {
            "description": "Request Entity Too Large",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['single_image.not_lt']['message']}}}
        }
    }
)
async def update_brand(
    brand_id: int = Path(...,gt=0),
    name: str = Form(...,min_length=2,max_length=100),
    file: UploadFile = Depends(single_image_optional),
    authorize: AuthJWT = Depends()
):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if brand := await BrandFetch.filter_by_id(brand_id):
        if brand['name'] != name and await BrandFetch.filter_by_name(name):
            raise HTTPException(status_code=400,detail=HttpError[lang]['brands.name_taken'])

        data = {"name": name}
        # delete the image from db if file exists
        if file:
            MagicImage.delete_image(file=brand['image'],path_delete='brands/')
            magic_image = MagicImage(file=file.file,width=200,height=200,path_upload='brands/',square=True)
            magic_image.save_image()
            data.update({"image": magic_image.file_name})

        await BrandCrud.update_brand(brand['id'],**data)
        return ResponseMessages[lang]['update_brand'][200]
    raise HTTPException(status_code=404,detail=HttpError[lang]['brands.not_found'])

@router.delete('/delete/{brand_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['delete_brand'][200]}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Brand not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['brands.not_found']['message']}}}
        }
    }
)
async def delete_brand(brand_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if brand := await BrandFetch.filter_by_id(brand_id):
        MagicImage.delete_image(file=brand['image'],path_delete='brands/')
        await BrandCrud.delete_brand(brand['id'])
        return ResponseMessages[lang]['delete_brand'][200]
    raise HTTPException(status_code=404,detail=HttpError[lang]['brands.not_found'])
