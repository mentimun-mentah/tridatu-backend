import json
from fastapi import APIRouter, Request, Path, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from controllers.UserController import UserFetch
from controllers.ProductController import ProductFetch, ProductCrud, ProductLogic
from controllers.VariantController import VariantFetch, VariantCrud, VariantLogic
from schemas.discounts.DiscountSchema import DiscountCreate, DiscountUpdate, DiscountDataProduct, DiscountPaginate
from schemas.variants.VariantSchema import VariantCreateUpdate
from dependencies.DiscountDependant import get_all_query_discount
from pytz import timezone
from config import settings

router = APIRouter()

tz = timezone(settings.timezone)

exclude_keys = {
    'va1_items': {
        '__all__': {
            'va1_discount': ...,
            'va1_discount_active': ...,
            'va2_items': {
                '__all__': {
                    'va2_discount',
                    'va2_discount_active',
                }
            }
        }
    }
}

@router.get('/all-discounts',response_model=DiscountPaginate,
    responses={
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail":"Only users with admin privileges can do this action."}}}
        }
    }
)
async def get_all_discounts(query_string: get_all_query_discount = Depends(), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    return await ProductFetch.get_all_discounts_paginate(**query_string)

@router.get('/get-discount/{product_id}',
    response_model=DiscountDataProduct,
    response_model_exclude_none=True,
    responses={
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail":"Only users with admin privileges can do this action."}}}
        },
        404: {
            "description": "Product not found",
            "content": {"application/json": {"example": {"detail":"Product not found!"}}}
        }
    }
)
async def get_discount_product(product_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    if product := await ProductFetch.filter_by_id(product_id):
        product_data = {f"products_{index}":value for index,value in product.items() if index in ['name','discount_start','discount_end']}
        product_data.update({'products_variant': await VariantFetch.get_variant_by_product_id(product['id'])})
        return product_data
    raise HTTPException(status_code=404,detail="Product not found!")

@router.post('/create',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully set discount on product."}}}
        },
        400: {
            "description": "Variant not same with product & Product already has discount",
            "content": {"application/json":{"example": {"detail":"string"}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail":"Only users with admin privileges can do this action."}}}
        },
        404: {
            "description": "Product & Ticket variant not found",
            "content": {"application/json": {"example": {"detail":"string"}}}
        }
    }
)
async def create_discount_product(request: Request, discount_data: DiscountCreate, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    redis_conn = request.app.state.redis

    if product := await ProductFetch.filter_by_id(discount_data.product_id):
        if redis_conn.get(discount_data.ticket_variant) is None:
            raise HTTPException(status_code=404,detail="Ticket variant not found!")
        if product['discount_start'] is not None and product['discount_end'] is not None:
            raise HTTPException(status_code=400,detail="Product already has discount.")

        variant_data_db = await VariantFetch.get_variant_by_product_id(product['id'])
        variant_data_input = json.loads(redis_conn.get(discount_data.ticket_variant))
        variant_db = VariantCreateUpdate.parse_obj(variant_data_db).dict(exclude=exclude_keys,exclude_none=True)
        variant_input = VariantCreateUpdate.parse_obj(variant_data_input).dict(exclude=exclude_keys,exclude_none=True)

        if variant_db != variant_input:
            raise HTTPException(status_code=400,detail="Variant not same with product.")

        variant_discount = VariantLogic.convert_data_to_db(variant_data_input,product['id'])

        # create variant with discount
        if len([1 for item in variant_discount if 'discount' in item and 'discount_active' in item]) > 0:
            discount_data.discount_start = discount_data.discount_start.replace(tzinfo=None)
            discount_data.discount_end = discount_data.discount_end.replace(tzinfo=None)

            await ProductCrud.update_product(product['id'],**discount_data.dict(include={'discount_start','discount_end'}))
            await VariantCrud.delete_variant(product['id'])
            await VariantCrud.create_variant(variant_discount)

        return {"detail": "Successfully set discount on product."}
    raise HTTPException(status_code=404,detail="Product not found!")

@router.put('/update',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully updated discount on product."}}}
        },
        400: {
            "description": "Must set discount before update it & Variant not same with product",
            "content": {"application/json":{"example": {"detail":"string"}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail":"Only users with admin privileges can do this action."}}}
        },
        404: {
            "description": "Product & Ticket variant not found",
            "content": {"application/json": {"example": {"detail":"string"}}}
        }
    }
)
async def update_discount_product(request: Request, discount_data: DiscountUpdate, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    redis_conn = request.app.state.redis

    if product := await ProductFetch.filter_by_id(discount_data.product_id):
        discount_db = [{index:value for index,value in product.items() if index in ['discount_start','discount_end']}]
        discount_db = ProductLogic.set_discount_status(discount_db)[0]

        discount_start, discount_end, discount_status = discount_db['discount_start'], discount_db['discount_end'], discount_db['discount_status']

        if redis_conn.get(discount_data.ticket_variant) is None:
            raise HTTPException(status_code=404,detail="Ticket variant not found!")
        if discount_start is None and discount_end is None:
            raise HTTPException(status_code=400,detail="You must set a discount on the product before update it.")

        # validation variant input
        variant_data_db = await VariantFetch.get_variant_by_product_id(product['id'])
        variant_data_input = json.loads(redis_conn.get(discount_data.ticket_variant))
        variant_db = VariantCreateUpdate.parse_obj(variant_data_db).dict(exclude=exclude_keys,exclude_none=True)
        variant_input = VariantCreateUpdate.parse_obj(variant_data_input).dict(exclude=exclude_keys,exclude_none=True)

        if variant_db != variant_input:
            raise HTTPException(status_code=400,detail="Variant not same with product.")

        # validation period promo
        discount_start, discount_end = tz.localize(discount_start), tz.localize(discount_end)
        # set input to data from db when promo is ongoing
        if discount_status == 'ongoing':
            discount_data.discount_start = discount_start

        discount_between = (discount_data.discount_end - discount_data.discount_start)

        if discount_start > discount_data.discount_start:
            raise HTTPException(status_code=422,detail="The new start time must be after the set start time.")
        if (round(discount_between.seconds / 3600, 2) < 1 and discount_between.days < 1) or discount_start > discount_data.discount_end:
            raise HTTPException(status_code=422,detail="The expiration time must be at least one hour longer than the start time.")
        if discount_between.days > 180:
            raise HTTPException(status_code=422,detail="Promo period must be less than 180 days.")

        # update data
        variant_discount = VariantLogic.convert_data_to_db(variant_data_input,product['id'])
        discount_data.discount_start = discount_data.discount_start.replace(tzinfo=None)
        discount_data.discount_end = discount_data.discount_end.replace(tzinfo=None)

        if len([1 for item in variant_discount if 'discount' in item and 'discount_active' in item]) == 0:
            discount_data.discount_start, discount_data.discount_end = None, None

        await ProductCrud.update_product(product['id'],**discount_data.dict(include={'discount_start','discount_end'}))
        await VariantCrud.delete_variant(product['id'])
        await VariantCrud.create_variant(variant_discount)

        return {"detail": "Successfully updated discount on product."}
    raise HTTPException(status_code=404,detail="Product not found!")

@router.delete('/non-active/{product_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully unset discount on the product."}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail":"Only users with admin privileges can do this action."}}}
        },
        404: {
            "description": "Product not found",
            "content": {"application/json": {"example": {"detail":"Product not found!"}}}
        }
    }
)
async def non_active_discount(product_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    if product := await ProductFetch.filter_by_id(product_id):
        variant_data_db = await VariantFetch.get_variant_by_product_id(product['id'])
        variant_db = VariantCreateUpdate.parse_obj(variant_data_db).dict(exclude=exclude_keys,exclude_none=True)
        variant_discount = VariantLogic.convert_data_to_db(variant_db,product['id'])

        await ProductCrud.update_product(product['id'],**{'discount_start': None, 'discount_end': None})
        await VariantCrud.delete_variant(product['id'])
        await VariantCrud.create_variant(variant_discount)

        return {"detail": "Successfully unset discount on the product."}
    raise HTTPException(status_code=404,detail="Product not found!")
