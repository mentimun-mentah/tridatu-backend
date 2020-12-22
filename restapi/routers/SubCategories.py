from fastapi import APIRouter, Depends, Path, HTTPException
from fastapi_jwt_auth import AuthJWT
from controllers.SubCategoryController import SubCategoryFetch, SubCategoryCrud
from controllers.CategoryController import CategoryFetch
from controllers.UserController import UserFetch
from schemas.sub_categories.SubCategorySchema import SubCategoryCreateUpdate, SubCategoryData
from typing import List

router = APIRouter()

@router.post('/create',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully add a new sub-category."}}}
        },
        400: {
            "description": "Name already taken",
            "content": {"application/json":{"example": {"detail":"The name has already been taken in sub category."}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail":"Only users with admin privileges can do this action."}}}
        },
        404: {
            "description": "Category not found",
            "content": {"application/json": {"example": {"detail":"Category not found!"}}}
        }
    }
)
async def create_sub_category(sub_category: SubCategoryCreateUpdate, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    if not await CategoryFetch.filter_by_id(sub_category.category_id):
        raise HTTPException(status_code=404,detail="Category not found!")

    if await SubCategoryFetch.check_duplicate_name(sub_category.category_id,sub_category.name):
        raise HTTPException(status_code=400,detail="The name has already been taken in sub category.")

    await SubCategoryCrud.create_sub_category(**sub_category.dict())
    return {"detail": "Successfully add a new sub-category."}

@router.get('/all-sub-categories',response_model=List[SubCategoryData])
async def get_all_sub_categories():
    return await SubCategoryFetch.get_all_sub_categories()

@router.get('/get-sub-category/{sub_category_id}',response_model=SubCategoryData,
    responses={
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail":"Only users with admin privileges can do this action."}}}
        },
        404: {
            "description": "Sub-category not found",
            "content": {"application/json": {"example": {"detail":"Sub-category not found!"}}}
        }
    }
)
async def get_sub_category_by_id(sub_category_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    if sub_category := await SubCategoryFetch.filter_by_id(sub_category_id):
        return {index:value for index,value in sub_category.items()}
    raise HTTPException(status_code=404,detail="Sub-category not found!")

@router.put('/update/{sub_category_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully update the sub-category."}}}
        },
        400: {
            "description": "Name already taken",
            "content": {"application/json":{"example": {"detail":"The name has already been taken in sub category."}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail":"Only users with admin privileges can do this action."}}}
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

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    if sub_category := await SubCategoryFetch.filter_by_id(sub_category_id):
        if not await CategoryFetch.filter_by_id(sub_category_data.category_id):
            raise HTTPException(status_code=404,detail="Category not found!")

        if await SubCategoryFetch.check_duplicate_name(sub_category_data.category_id,sub_category_data.name):
            raise HTTPException(status_code=400,detail="The name has already been taken in sub category.")

        data = {
            "name": sub_category_data.name,
            "category_id": sub_category_data.category_id
        }

        await SubCategoryCrud.update_sub_category(sub_category['id'],**data)
        return {"detail": "Successfully update the sub-category."}
    raise HTTPException(status_code=404,detail="Sub-category not found!")

@router.delete('/delete/{sub_category_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully delete the sub-category."}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail":"Only users with admin privileges can do this action."}}}
        },
        404: {
            "description": "Sub-category not found",
            "content": {"application/json": {"example": {"detail":"Sub-category not found!"}}}
        }
    }
)
async def delete_sub_category(sub_category_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    if sub_category := await SubCategoryFetch.filter_by_id(sub_category_id):
        await SubCategoryCrud.delete_sub_category(sub_category['id'])
        return {"detail": "Successfully delete the sub-category."}
    raise HTTPException(status_code=404,detail="Sub-category not found!")
