from fastapi import APIRouter, Depends, Path, HTTPException
from fastapi_jwt_auth import AuthJWT
from controllers.ItemSubCategoryController import ItemSubCategoryFetch, ItemSubCategoryCrud
from controllers.SubCategoryController import SubCategoryFetch
from controllers.UserController import UserFetch
from schemas.item_sub_categories.ItemSubCategorySchema import ItemSubCategoryCreateUpdate, ItemSubCategoryData
from typing import List

router = APIRouter()

@router.post('/create',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully add a new item sub-category."}}}
        },
        400: {
            "description": "Name already taken",
            "content": {"application/json":
                {"example": {"detail":"The name has already been taken in the item sub-category."}}
            }
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail":"Only users with admin privileges can do this action."}}}
        },
        404: {
            "description": "Sub-category not found",
            "content": {"application/json": {"example": {"detail": "Sub-category not found!"}}}
        }
    }
)
async def create_item_sub_category(item_sub_category: ItemSubCategoryCreateUpdate, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    if not await SubCategoryFetch.filter_by_id(item_sub_category.sub_category_id):
        raise HTTPException(status_code=404,detail="Sub-category not found!")

    if await ItemSubCategoryFetch.check_duplicate_name(
        item_sub_category.sub_category_id,
        item_sub_category.name_item_sub_category
    ):
        raise HTTPException(status_code=400,detail="The name has already been taken in the item sub-category.")

    await ItemSubCategoryCrud.create_item_sub_category(**item_sub_category.dict())
    return {"detail": "Successfully add a new item sub-category."}

@router.get('/all-item-sub-categories',response_model=List[ItemSubCategoryData])
async def get_all_item_sub_categories():
    return await ItemSubCategoryFetch.get_all_item_sub_categories()

@router.get('/get-item-sub-category/{item_sub_category_id}',response_model=ItemSubCategoryData,
    responses={
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail":"Only users with admin privileges can do this action."}}}
        },
        404: {
            "description": "Item sub-category not found",
            "content": {"application/json": {"example": {"detail":"Item sub-category not found!"}}}
        }
    }
)
async def get_item_sub_category_by_id(item_sub_category_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    if item_sub_category := await ItemSubCategoryFetch.filter_by_id(item_sub_category_id):
        return {index:value for index,value in item_sub_category.items()}
    raise HTTPException(status_code=404,detail="Item sub-category not found!")

@router.put('/update/{item_sub_category_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully update the item sub-category."}}}
        },
        400: {
            "description": "Name already taken",
            "content": {"application/json":
                {"example": {"detail":"The name has already been taken in the item sub-category."}}
            }
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail":"Only users with admin privileges can do this action."}}}
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

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    if item_sub_category := await ItemSubCategoryFetch.filter_by_id(item_sub_category_id):
        if not await SubCategoryFetch.filter_by_id(item_sub_category_data.sub_category_id):
            raise HTTPException(status_code=404,detail="Sub-category not found!")

        if await ItemSubCategoryFetch.check_duplicate_name(
            item_sub_category_data.sub_category_id,
            item_sub_category_data.name_item_sub_category
        ):
            raise HTTPException(status_code=400,detail="The name has already been taken in the item sub-category.")

        data = {
            "name_item_sub_category": item_sub_category_data.name_item_sub_category,
            "sub_category_id": item_sub_category_data.sub_category_id
        }

        await ItemSubCategoryCrud.update_item_sub_category(item_sub_category['id_item_sub_category'],**data)
        return {"detail": "Successfully update the item sub-category."}
    raise HTTPException(status_code=404,detail="Item sub-category not found!")

@router.delete('/delete/{item_sub_category_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully delete the item sub-category."}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail":"Only users with admin privileges can do this action."}}}
        },
        404: {
            "description": "Item sub-category not found",
            "content": {"application/json": {"example": {"detail":"Item sub-category not found!"}}}
        }
    }
)
async def delete_item_sub_category(item_sub_category_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    if item_sub_category := await ItemSubCategoryFetch.filter_by_id(item_sub_category_id):
        await ItemSubCategoryCrud.delete_item_sub_category(item_sub_category['id_item_sub_category'])
        return {"detail": "Successfully delete the item sub-category."}
    raise HTTPException(status_code=404,detail="Item sub-category not found!")
