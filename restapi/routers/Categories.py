from fastapi import APIRouter, Depends, Query, Path, HTTPException
from fastapi_jwt_auth import AuthJWT
from controllers.CategoryController import CategoryFetch, CategoryCrud
from controllers.UserController import UserFetch
from schemas.categories.CategorySchema import (
    CategoryCreateUpdate,
    CategoryData,
    CategoryDataWithoutLabels,
    CategoryWithChildrenData
)
from localization import LocalizationRoute
from I18N import ResponseMessages, HttpError
from config import settings
from typing import List

router = APIRouter(route_class=LocalizationRoute)
# default language response
lang = settings.default_language_code

@router.post('/create',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['create_category'][201]}}
        },
        400: {
            "description": "Name already taken",
            "content": {"application/json":{"example": {"detail": HttpError[lang]['categories.name_taken']['message']}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        }
    }
)
async def create_category(category: CategoryCreateUpdate, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if await CategoryFetch.filter_by_name(category.name):
        raise HTTPException(status_code=400,detail=HttpError[lang]['categories.name_taken'])

    await CategoryCrud.create_category(category.name)
    return ResponseMessages[lang]['create_category'][201]

@router.get('/',response_model=List[CategoryWithChildrenData])
async def get_categories_with_children(q: str = Query(None,min_length=1)):
    return await CategoryFetch.get_categories_with_children(q)

@router.get('/all-categories',response_model=List[CategoryData], response_model_exclude_none=True)
async def get_all_categories(with_sub: bool = Query(...), q: str = Query(None,min_length=1)):
    return await CategoryFetch.get_all_categories(with_sub,q)

@router.get('/get-category/{category_id}',response_model=CategoryDataWithoutLabels,
    responses={
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Category not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['categories.not_found']['message']}}}
        }
    }
)
async def get_category_by_id(category_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if category := await CategoryFetch.filter_by_id(category_id):
        return {index:value for index,value in category.items()}
    raise HTTPException(status_code=404,detail=HttpError[lang]['categories.not_found'])

@router.put('/update/{category_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['update_category'][200]}}
        },
        400: {
            "description": "Name already taken",
            "content": {"application/json":{"example": {"detail": HttpError[lang]['categories.name_taken']['message']}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Category not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['categories.not_found']['message']}}}
        }
    }
)
async def update_category(
    category_data: CategoryCreateUpdate,
    category_id: int = Path(...,gt=0),
    authorize: AuthJWT = Depends()
):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if category := await CategoryFetch.filter_by_id(category_id):
        if category['name'] != category_data.name and await CategoryFetch.filter_by_name(category_data.name):
            raise HTTPException(status_code=400,detail=HttpError[lang]['categories.name_taken'])

        await CategoryCrud.update_category(category['id'],name=category_data.name)
        return ResponseMessages[lang]['update_category'][200]
    raise HTTPException(status_code=404,detail=HttpError[lang]['categories.not_found'])

@router.delete('/delete/{category_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['delete_category'][200]}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Category not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['categories.not_found']['message']}}}
        }
    }
)
async def delete_category(category_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if category := await CategoryFetch.filter_by_id(category_id):
        await CategoryCrud.delete_category(category['id'])
        return ResponseMessages[lang]['delete_category'][200]
    raise HTTPException(status_code=404,detail=HttpError[lang]['categories.not_found'])
