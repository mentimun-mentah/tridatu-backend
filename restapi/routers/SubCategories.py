from fastapi import APIRouter, Depends, Path, HTTPException
from fastapi_jwt_auth import AuthJWT
from controllers.SubCategoryController import SubCategoryFetch, SubCategoryCrud
from controllers.CategoryController import CategoryFetch
from controllers.UserController import UserFetch
from schemas.sub_categories.SubCategorySchema import SubCategoryCreateUpdate, SubCategoryData
from localization import LocalizationRoute
from I18N import ResponseMessages, HttpError
from config import settings

router = APIRouter(route_class=LocalizationRoute)
# default language response
lang = settings.default_language_code

@router.post('/create',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['create_sub_category'][201]}}
        },
        400: {
            "description": "Name already taken",
            "content": {"application/json":{"example": {"detail": HttpError[lang]['sub_categories.name_taken']['message']}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Category not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['sub_categories.category_not_found']['message']}}}
        }
    }
)
async def create_sub_category(sub_category: SubCategoryCreateUpdate, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if not await CategoryFetch.filter_by_id(sub_category.category_id):
        raise HTTPException(status_code=404,detail=HttpError[lang]['sub_categories.category_not_found'])

    if await SubCategoryFetch.check_duplicate_name(sub_category.category_id,sub_category.name):
        raise HTTPException(status_code=400,detail=HttpError[lang]['sub_categories.name_taken'])

    await SubCategoryCrud.create_sub_category(**sub_category.dict())
    return ResponseMessages[lang]['create_sub_category'][201]

@router.get('/get-sub-category/{sub_category_id}',response_model=SubCategoryData,
    responses={
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Sub-category not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['sub_categories.not_found']['message']}}}
        }
    }
)
async def get_sub_category_by_id(sub_category_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if sub_category := await SubCategoryFetch.filter_by_id(sub_category_id):
        return {index:value for index,value in sub_category.items()}
    raise HTTPException(status_code=404,detail=HttpError[lang]['sub_categories.not_found'])

@router.put('/update/{sub_category_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['update_sub_category'][200]}}
        },
        400: {
            "description": "Name already taken",
            "content": {"application/json":{"example": {"detail": HttpError[lang]['sub_categories.name_taken']['message']}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Sub-category or Category not found",
            "content": {"application/json": {"example": {"detail":"string"}}}
        }
    }
)
async def update_sub_category(
    sub_category_data: SubCategoryCreateUpdate,
    sub_category_id: int = Path(...,gt=0),
    authorize: AuthJWT = Depends()
):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if sub_category := await SubCategoryFetch.filter_by_id(sub_category_id):
        if not await CategoryFetch.filter_by_id(sub_category_data.category_id):
            raise HTTPException(status_code=404,detail=HttpError[lang]['sub_categories.category_not_found'])

        if await SubCategoryFetch.check_duplicate_name(sub_category_data.category_id,sub_category_data.name):
            raise HTTPException(status_code=400,detail=HttpError[lang]['sub_categories.name_taken'])

        data = {
            "name": sub_category_data.name,
            "category_id": sub_category_data.category_id
        }

        await SubCategoryCrud.update_sub_category(sub_category['id'],**data)
        return ResponseMessages[lang]['update_sub_category'][200]
    raise HTTPException(status_code=404,detail=HttpError[lang]['sub_categories.not_found'])

@router.delete('/delete/{sub_category_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['delete_sub_category'][200]}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Sub-category not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['sub_categories.not_found']['message']}}}
        }
    }
)
async def delete_sub_category(sub_category_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if sub_category := await SubCategoryFetch.filter_by_id(sub_category_id):
        await SubCategoryCrud.delete_sub_category(sub_category['id'])
        return ResponseMessages[lang]['delete_sub_category'][200]
    raise HTTPException(status_code=404,detail=HttpError[lang]['sub_categories.not_found'])
