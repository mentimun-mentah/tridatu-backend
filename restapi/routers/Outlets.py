from fastapi import APIRouter, Depends, UploadFile, Path, HTTPException
from fastapi_jwt_auth import AuthJWT
from controllers.OutletController import OutletCrud, OutletFetch
from controllers.UserController import UserFetch
from schemas.outlets.OutletSchema import OutletSchema
from libs.MagicImage import MagicImage, SingleImageRequired
from typing import List

router = APIRouter()

# dependencies injection for validation an image
single_image_required = SingleImageRequired(
    max_file_size=4,
    allow_file_ext=['jpg','png','jpeg']
)

@router.post('/create',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully add a new outlet."}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail":"Only users with admin privileges can do this action."}}}
        },
        413: {
            "description": "Request Entity Too Large",
            "content": {"application/json": {"example": {"detail":"An image cannot greater than 4 Mb."}}}
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
    return {"detail": "Successfully add a new outlet."}

@router.get('/all-outlets',response_model=List[OutletSchema])
async def get_all_outlets():
    return await OutletFetch.get_all_outlets()

@router.delete('/delete/{outlet_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json": {"example": {"detail":"Successfully delete the outlet."}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail":"Only users with admin privileges can do this action."}}}
        },
        404: {
            "description": "Outlet not found",
            "content": {"application/json": {"example": {"detail":"Outlet not found!"}}}
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
        return {"detail": "Successfully delete the outlet."}
    raise HTTPException(status_code=404,detail="Outlet not found!")
