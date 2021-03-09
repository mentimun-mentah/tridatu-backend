from fastapi import APIRouter, Response, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from controllers.CartController import CartFetch, CartCrud
from controllers.UserController import UserFetch
from controllers.VariantController import VariantFetch
from controllers.WishlistController import WishlistCrud, WishlistLogic
from schemas.carts.CartSchema import CartCreateUpdate, CartDelete, CartData, CartDataNav, CartQtyItemData
from dependencies.CartDependant import get_all_query_cart
from localization import LocalizationRoute
from I18N import ResponseMessages, HttpError
from config import settings
from typing import List

router = APIRouter(route_class=LocalizationRoute)
# default language response
lang = settings.default_language_code

@router.post('/put-product',status_code=201,
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['put_product_to_cart'][200]}}
        },
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['put_product_to_cart'][201]}}
        },
        400: {
            "description": "Qty greater than stock product & Cart can only contain 20 items",
            "content": {"application/json": {"example": {"detail": "string"}}}
        },
        404: {
            "description": "Variant not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['carts.variant_not_found']['message']}}}
        }
    }
)
async def put_product_to_cart(res: Response, cart_data: CartCreateUpdate, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    if user := await UserFetch.filter_by_id(user_id):
        if variant := await VariantFetch.filter_by_id(cart_data.variant_id):
            cart_total = await CartFetch.get_qty_and_item_on_cart(user['id'])
            cart_db = await CartFetch.filter_by_user_variant(user['id'],variant['id'])

            cart_qty = cart_data.qty
            if cart_db and cart_data.operation == 'create':
                cart_qty += cart_db['qty']

            if cart_qty > variant['stock']:
                msg = HttpError[lang]['carts.stock_not_enough_1']
                if cart_db:
                    msg = HttpError[lang]['carts.stock_not_enough_2']
                    msg['ctx'].update({'stock': variant['stock'], 'qty': cart_db['qty']})

                raise HTTPException(status_code=400,detail=msg)

            # update data before update or create cart
            kwargs = cart_data.dict(exclude={'operation'})
            kwargs.update({'user_id': user['id'], 'qty': cart_qty})

            if cart_db:
                res.status_code = 200
                await CartCrud.update_cart(cart_db['id'],**kwargs)
                return ResponseMessages[lang]['put_product_to_cart'][200]

            if cart_total['total_item'] >= 20:
                raise HTTPException(status_code=400,detail=HttpError[lang]['carts.max_items'])

            await CartCrud.create_cart(**kwargs)
            return ResponseMessages[lang]['put_product_to_cart'][201]
        raise HTTPException(status_code=404,detail=HttpError[lang]['carts.variant_not_found'])

@router.get('/qty-item-on-cart',response_model=CartQtyItemData)
async def get_qty_and_item_on_cart(authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    if user := await UserFetch.filter_by_id(user_id):
        return await CartFetch.get_qty_and_item_on_cart(user['id'])

@router.get('/from-nav',response_model=List[CartDataNav])
async def get_all_carts_from_nav(authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    if user := await UserFetch.filter_by_id(user_id):
        return await CartFetch.get_all_carts_from_nav(user['id'])

@router.get('/',response_model=List[CartData])
async def get_all_carts(query_string: get_all_query_cart = Depends(), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    if user := await UserFetch.filter_by_id(user_id):
        results = await CartFetch.get_all_carts(user['id'], **query_string)
        [
            data.__setitem__('products_love',await WishlistLogic.check_wishlist(data['products_id'],user_id))
            for data in results
        ]
        return results

@router.post('/delete',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['delete_cart'][200]}}
        }
    }
)
async def delete_cart(cart_data: CartDelete, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    if user := await UserFetch.filter_by_id(user_id):
        await CartCrud.delete_cart(user['id'],cart_data.cartIds)
        response = ResponseMessages[lang]['delete_cart'][200].copy()
        response.update({'ctx': {'item': len(cart_data.cartIds)}})
        return response

@router.post('/move-to-wishlist',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['move_to_wishlist'][200]}}
        }
    }
)
async def move_to_wishlist(cart_data: CartDelete, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    if user := await UserFetch.filter_by_id(user_id):
        # move variant-product to wishlist
        products_id = await CartFetch.get_all_carts_product_id(user['id'],cart_data.cartIds)
        wishlist_data = [{'product_id': id_, 'user_id': user['id']} for id_ in products_id]
        await WishlistCrud.create_wishlist_many(wishlist_data)
        # delete variant on cart
        await CartCrud.delete_cart(user['id'],cart_data.cartIds)

        response = ResponseMessages[lang]['move_to_wishlist'][200].copy()
        response.update({'ctx': {'item': len(cart_data.cartIds)}})
        return response
