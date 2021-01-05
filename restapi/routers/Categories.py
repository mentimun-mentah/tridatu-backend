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
from typing import List

router = APIRouter()

@router.post('/create',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully add a new category."}}}
        },
        400: {
            "description": "Name already taken",
            "content": {"application/json":{"example": {"detail":"The name has already been taken."}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail":"Only users with admin privileges can do this action."}}}
        }
    }
)
async def create_category(category: CategoryCreateUpdate, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    if await CategoryFetch.filter_by_name(category.name):
        raise HTTPException(status_code=400,detail="The name has already been taken.")

    await CategoryCrud.create_category(category.name)
    return {"detail": "Successfully add a new category."}

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
            "content": {"application/json": {"example": {"detail":"Only users with admin privileges can do this action."}}}
        },
        404: {
            "description": "Category not found",
            "content": {"application/json": {"example": {"detail":"Category not found!"}}}
        }
    }
)
async def get_category_by_id(category_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    if category := await CategoryFetch.filter_by_id(category_id):
        return {index:value for index,value in category.items()}
    raise HTTPException(status_code=404,detail="Category not found!")

@router.put('/update/{category_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully update the category."}}}
        },
        400: {
            "description": "Name already taken",
            "content": {"application/json":{"example": {"detail":"The name has already been taken."}}}
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
async def update_category(
    category_data: CategoryCreateUpdate,
    category_id: int = Path(...,gt=0),
    authorize: AuthJWT = Depends()
):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    if category := await CategoryFetch.filter_by_id(category_id):
        if category['name'] != category_data.name and await CategoryFetch.filter_by_name(category_data.name):
            raise HTTPException(status_code=400,detail="The name has already been taken.")

        await CategoryCrud.update_category(category['id'],name=category_data.name)
        return {"detail": "Successfully update the category."}
    raise HTTPException(status_code=404,detail="Category not found!")

@router.delete('/delete/{category_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully delete the category."}}}
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
async def delete_category(category_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    if category := await CategoryFetch.filter_by_id(category_id):
        await CategoryCrud.delete_category(category['id'])
        return {"detail": "Successfully delete the category."}
    raise HTTPException(status_code=404,detail="Category not found!")
