import json
from fastapi import APIRouter, Query, Path, Depends, HTTPException
from fastapi.requests import Request
from fastapi_jwt_auth import AuthJWT
from controllers.ProductController import ProductFetch, ProductCrud
from controllers.VariantController import VariantLogic, VariantCrud
from controllers.ItemSubCategoryController import ItemSubCategoryFetch
from controllers.WishlistController import WishlistLogic
from controllers.BrandController import BrandFetch
from controllers.UserController import UserFetch
from dependencies.ProductDependant import create_form_product, get_all_query_product
from schemas.products.ProductSchema import ProductPaginate, ProductSearchByName, ProductDataSlug
from models.ProductModel import product
from libs.MagicImage import MagicImage
from libs.Visitor import Visitor
from slugify import slugify
from typing import List

router = APIRouter()

@router.post('/create',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully add a new product."}}}
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
            "description": "Item sub-category, Brand, Ticket variant not found",
            "content": {"application/json": {"example": {"detail":"string"}}}
        },
        409: {
            "description": "Conflict",
            "content": {"application/json": {"example": {"detail":"Each image must be unique."}}}
        },
        413: {
            "description": "Request Entity Too Large",
            "content": {"application/json": {"example": {"detail":"An image cannot greater than 4 Mb."}}}
        }
    }
)
async def create_product(form_data: create_form_product = Depends(), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    form_data['slug'] = slugify(form_data['name'])

    # check name duplicate
    if await ProductFetch.filter_by_slug(form_data['slug']):
        raise HTTPException(status_code=400,detail="The name has already been taken.")
    # check item_sub_category_id exists in db
    if not await ItemSubCategoryFetch.filter_by_id(form_data['item_sub_category_id']):
        raise HTTPException(status_code=404,detail="Item sub-category not found!")
    # check brand exists in db if data supplied
    if form_data['brand_id'] and not await BrandFetch.filter_by_id(form_data['brand_id']):
        raise HTTPException(status_code=404,detail="Brand not found!")

    # save image products to storage
    image_magic_products = MagicImage(
        square=True,
        file=form_data['image_product'],
        width=550,
        height=550,
        path_upload='products/',
        dir_name=form_data['slug']
    )
    image_magic_products.save_image()
    form_data['image_product'] = json.dumps(image_magic_products.file_name)

    # save image variants to product folder if supplied
    if image_variant := form_data['image_variant']:
        image_magic_variants = MagicImage(
            square=True,
            file=image_variant,
            width=550,
            height=550,
            path_upload='products/',
            dir_name=form_data['slug']
        )
        image_magic_variants.save_image()
        form_data['image_variant'] = image_magic_variants.file_name

        for index, value in form_data['image_variant'].items():
            form_data['variant_data']['va1_items'][index]['va1_image'] = value

    # save image size guide to product folder if supplied
    if image_size_guide := form_data['image_size_guide']:
        image_magic_guide = MagicImage(
            file=image_size_guide.file,
            width=1200,
            height=778,
            path_upload='products/',
            dir_name=form_data['slug']
        )
        image_magic_guide.save_image()
        form_data['image_size_guide'] = image_magic_guide.file_name

    # save product to db
    product_data = {
        index:value for index, value in form_data.items() if index != 'variant_data' and index != 'image_variant'
    }
    product_id = await ProductCrud.create_product(**product_data)

    # save variant to db
    variant_db = VariantLogic.convert_data_to_db(form_data['variant_data'],product_id)
    await VariantCrud.create_variant(variant_db)

    return {"detail": "Successfully add a new product."}

@router.get('/all-products',response_model=ProductPaginate)
async def get_all_products(query_string: get_all_query_product = Depends(), authorize: AuthJWT = Depends()):
    authorize.jwt_optional()

    results = await ProductFetch.get_all_products_paginate(**query_string)
    if user_id := authorize.get_jwt_subject():
        [
            data.__setitem__('products_love',await WishlistLogic.check_wishlist(data['products_id'],user_id))
            for data in results['data']
        ]
    else:
        [data.__setitem__('products_love',False) for data in results['data']]

    return results

@router.put('/alive-archive/{product_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully change the product to 'alive'/'archive'."}}}
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
async def change_product_alive_archive(product_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    await UserFetch.user_is_admin(user_id)

    if product := await ProductFetch.filter_by_id(product_id):
        await ProductCrud.change_product_alive_archive(product['id'],product['live'])
        msg = 'alive' if not product['live'] else 'archive'
        return {"detail": f"Successfully change the product to {msg}."}
    raise HTTPException(status_code=404,detail="Product not found!")

@router.get('/search-by-name',response_model=List[ProductSearchByName])
async def search_products_by_name(q: str = Query(...,min_length=1), limit: int = Query(...,gt=0)):
    return await ProductFetch.search_products_by_name(q=q,limit=limit)

@router.get('/{slug}',
    response_model=ProductDataSlug,
    response_model_exclude_none=True,
    responses={
        404: {
            "description": "Product not found",
            "content": {"application/json": {"example": {"detail":"Product not found!"}}}
        }
    }
)
async def get_product_by_slug(
    request: Request,
    slug: str = Path(...,min_length=1),
    recommendation: bool = Query(...),
    authorize: AuthJWT = Depends(),
    visitor: Visitor = Depends()
):
    authorize.jwt_optional()

    # set redis conn from state
    redis = request.app.state.redis

    if product_data := await ProductFetch.filter_by_slug(slug):
        await visitor.increment_visitor(table=product,id_=product_data['id'])  # set visitor
        results = await ProductFetch.get_product_by_slug(product_data['slug'])
        # get product recommendation
        if recommendation is True:
            if redis.get(f"products_recommendation:{slug}") is None:
                results['products_recommendation'] = await ProductFetch.get_product_recommendation(limit=6)
                redis.set(
                    f"products_recommendation:{slug}",
                    json.dumps(results['products_recommendation'],default=str), 600
                )  # save product recommendation by slug in cache 10 minutes
            else:
                results['products_recommendation'] = json.loads(redis.get(f"products_recommendation:{slug}"))

        # check wishlist product & product recommendation
        if user_id := authorize.get_jwt_subject():
            results.__setitem__('products_love', await WishlistLogic.check_wishlist(product_data['id'],user_id))
            if recommendation is True:
                [
                    data.__setitem__('products_love',await WishlistLogic.check_wishlist(data['products_id'],user_id))
                    for data in results['products_recommendation']
                ]
        else:
            results.__setitem__('products_love', False)
            if recommendation is True:
                [data.__setitem__('products_love',False) for data in results['products_recommendation']]

        return results
    raise HTTPException(status_code=404,detail="Product not found!")
