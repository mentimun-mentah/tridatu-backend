from fastapi import APIRouter, Depends, Path, HTTPException
from fastapi_jwt_auth import AuthJWT
from controllers.ItemSubCategoryController import ItemSubCategoryFetch, ItemSubCategoryCrud
from controllers.SubCategoryController import SubCategoryFetch
from controllers.UserController import UserFetch
from schemas.item_sub_categories.ItemSubCategorySchema import ItemSubCategoryCreateUpdate, ItemSubCategoryData
from localization import LocalizationRoute, HttpError
from I18N import ResponseMessages
from config import settings

router = APIRouter(route_class=LocalizationRoute)
# default language response
lang = settings.default_language_code

@router.post('/create',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['create_item_sub_category'][201]}}
        },
        400: {
            "description": "Name already taken",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['item_sub_categories.name_taken']['message']}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Sub-category not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['item_sub_categories.sub_not_found']['message']}}}
        }
    }
)
async def create_item_sub_category(item_sub_category: ItemSubCategoryCreateUpdate, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if not await SubCategoryFetch.filter_by_id(item_sub_category.sub_category_id):
        raise HTTPException(status_code=404,detail=HttpError[lang]['item_sub_categories.sub_not_found'])

    if await ItemSubCategoryFetch.check_duplicate_name(item_sub_category.sub_category_id,item_sub_category.name):
        raise HTTPException(status_code=400,detail=HttpError[lang]['item_sub_categories.name_taken'])

    await ItemSubCategoryCrud.create_item_sub_category(**item_sub_category.dict())
    return ResponseMessages[lang]['create_item_sub_category'][201]

@router.get('/get-item-sub-category/{item_sub_category_id}',response_model=ItemSubCategoryData,
    responses={
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Item sub-category not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['item_sub_categories.not_found']['message']}}}
        }
    }
)
async def get_item_sub_category_by_id(item_sub_category_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if item_sub_category := await ItemSubCategoryFetch.filter_by_id(item_sub_category_id):
        return {index:value for index,value in item_sub_category.items()}
    raise HTTPException(status_code=404,detail=HttpError[lang]['item_sub_categories.not_found'])

@router.put('/update/{item_sub_category_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['update_item_sub_category'][200]}}
        },
        400: {
            "description": "Name already taken",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['item_sub_categories.name_taken']['message']}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Item sub-category or Sub-category not found",
            "content": {"application/json": {"example": {"detail":"string"}}}
        }
    }
)
async def update_item_sub_category(
    item_sub_category_data: ItemSubCategoryCreateUpdate,
    item_sub_category_id: int = Path(...,gt=0),
    authorize: AuthJWT = Depends()
):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if item_sub_category := await ItemSubCategoryFetch.filter_by_id(item_sub_category_id):
        if not await SubCategoryFetch.filter_by_id(item_sub_category_data.sub_category_id):
            raise HTTPException(status_code=404,detail=HttpError[lang]['item_sub_categories.sub_not_found'])

        if await ItemSubCategoryFetch.check_duplicate_name(
            item_sub_category_data.sub_category_id,
            item_sub_category_data.name
        ):
            raise HTTPException(status_code=400,detail=HttpError[lang]['item_sub_categories.name_taken'])

        data = {
            "name": item_sub_category_data.name,
            "sub_category_id": item_sub_category_data.sub_category_id
        }

        await ItemSubCategoryCrud.update_item_sub_category(item_sub_category['id'],**data)
        return ResponseMessages[lang]['update_item_sub_category'][200]
    raise HTTPException(status_code=404,detail=HttpError[lang]['item_sub_categories.not_found'])

@router.delete('/delete/{item_sub_category_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['delete_item_sub_category'][200]}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Item sub-category not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['item_sub_categories.not_found']['message']}}}
        }
    }
)
async def delete_item_sub_category(item_sub_category_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if item_sub_category := await ItemSubCategoryFetch.filter_by_id(item_sub_category_id):
        await ItemSubCategoryCrud.delete_item_sub_category(item_sub_category['id'])
        return ResponseMessages[lang]['delete_item_sub_category'][200]
    raise HTTPException(status_code=404,detail=HttpError[lang]['item_sub_categories.not_found'])
