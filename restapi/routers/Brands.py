from fastapi import APIRouter, Depends, UploadFile, Path, Form, HTTPException
from fastapi_jwt_auth import AuthJWT
from controllers.BrandController import BrandCrud, BrandFetch
from controllers.UserController import UserFetch
from libs.MagicImage import MagicImage, SingleImageRequired

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
            "content": {"application/json":{"example": {"detail":"Successfully add a new brand."}}}
        },
        400: {
            "description": "Name already taken",
            "content": {"application/json":{"example": {"detail":"The name has already been taken."}}}
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
async def create_brand(
    name: str = Form(...,min_length=2,max_length=100),
    file: UploadFile = Depends(single_image_required),
    authorize: AuthJWT = Depends()
):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    if await BrandFetch.filter_by_name(name):
        raise HTTPException(status_code=400,detail="The name has already been taken.")

    magic_image = MagicImage(file=file.file,width=200,height=200,path_upload='brands/',square=True)
    magic_image.save_image()

    await BrandCrud.create_brand(name,magic_image.file_name)
    return {"detail": "Successfully add a new brand."}

@router.get('/all-brands')
async def get_all_brands():
    pass

@router.get('/get-brand/{brand_id}')
async def get_brand_by_id(brand_id: int = Path(...,gt=0)):
    pass

@router.put('/update/{brand_id}')
async def update_brand(brand_id: int = Path(...,gt=0)):
    pass

@router.delete('/delete/{brand_id}')
async def delete_brand(brand_id: int = Path(...,gt=0)):
    pass
