from fastapi import APIRouter, Depends, Path, Response, HTTPException
from fastapi_jwt_auth import AuthJWT
from controllers.ProductController import ProductFetch
from controllers.WishlistController import WishlistLogic, WishlistCrud

router = APIRouter()

@router.post('/love/{product_id}',status_code=201,
    responses={
        200: {
            "description": "Product already on wishlists",
            "content": {"application/json": {"example": {"detail":"Product already on the wishlist."}}}
        },
        201: {
            "description": "Successful Response",
            "content": {"application/json": {"example": {"detail":"Product successfully added to wishlist."}}}
        },
        404: {
            "description": "Product not found",
            "content": {"application/json": {"example": {"detail":"Product not found!"}}}
        }
    }
)
async def love_product(res: Response, product_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    if product := await ProductFetch.filter_by_id(product_id):
        if not await WishlistLogic.check_wishlist(product['id_product'],user_id):
            await WishlistCrud.create_wishlist(product['id_product'],user_id)
            return {"detail": "Product successfully added to wishlist."}
        res.status_code = 200
        return {"detail":"Product already on the wishlist."}
    raise HTTPException(status_code=404,detail="Product not found!")

@router.delete('/unlove/{product_id}',
    responses={
        200: {
            "description": "Successfully removed or not on wishlist",
            "content": {"application/json": {"example": {"detail":"string"}}}
        },
        404: {
            "description": "Product not found",
            "content": {"application/json": {"example": {"detail":"Product not found!"}}}
        }
    }
)
async def unlove_product(product_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    if product := await ProductFetch.filter_by_id(product_id):
        if await WishlistLogic.check_wishlist(product['id_product'],user_id):
            await WishlistCrud.delete_wishlist(product['id_product'],user_id)
            return {"detail": "Product has been removed from the wishlist."}
        return {"detail": "Product not on the wishlist."}
    raise HTTPException(status_code=404,detail="Product not found!")
