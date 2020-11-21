from fastapi import APIRouter, Depends, Path, HTTPException
from fastapi_jwt_auth import AuthJWT
from controllers.SubCategoryController import SubCategoryFetch, SubCategoryCrud
from controllers.CategoryController import CategoryFetch
from controllers.UserController import UserFetch
from schemas.sub_categories.SubCategorySchema import SubCategoryCreateUpdate

router = APIRouter()

@router.post('/create',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully add a new sub-category."}}}
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
async def create_sub_category(sub_category: SubCategoryCreateUpdate, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    if not await CategoryFetch.filter_by_id(sub_category.category_id):
        raise HTTPException(status_code=404,detail="Category not found!")

    if await SubCategoryFetch.filter_by_name(sub_category.name_sub_category):
        raise HTTPException(status_code=400,detail="The name has already been taken.")

    await SubCategoryCrud.create_sub_category(**sub_category.dict())
    return {"detail": "Successfully add a new sub-category."}

@router.get('/all-sub-categories')
async def get_all_sub_categories():
    pass

@router.get('/get-sub-category/{sub_category_id}')
async def get_sub_category_by_id(sub_category_id: int = Path(...,gt=0)):
    pass

@router.put('/update/{sub_category_id}')
async def update_sub_category(sub_category_id: int = Path(...,gt=0)):
    pass

@router.delete('/delete/{sub_category_id}')
async def delete_sub_category(sub_category_id: int = Path(...,gt=0)):
    pass
