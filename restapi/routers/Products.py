import json
from fastapi import APIRouter, Query, Path, Depends, HTTPException
from fastapi.requests import Request
from fastapi_jwt_auth import AuthJWT
from controllers.ProductController import ProductFetch, ProductCrud
from controllers.VariantController import VariantLogic, VariantCrud, VariantFetch
from controllers.WholeSaleController import WholeSaleCrud, WholeSaleFetch
from controllers.ItemSubCategoryController import ItemSubCategoryFetch
from controllers.WishlistController import WishlistLogic
from controllers.BrandController import BrandFetch
from controllers.UserController import UserFetch
from dependencies.ProductDependant import (
    create_form_product,
    update_form_product,
    get_all_query_product
)
from schemas.products.ProductSchema import (
    ProductPaginate,
    ProductSearchByName,
    ProductDataSlug
)
from models.ProductModel import product
from libs.MagicImage import MagicImage
from libs.Visitor import Visitor
from localization import LocalizationRoute
from I18N import ResponseMessages, HttpError
from config import settings
from slugify import slugify
from typing import List

router = APIRouter(route_class=LocalizationRoute)
# default language response
lang = settings.default_language_code

@router.post('/create',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['create_product'][201]}}
        },
        400: {
            "description": "Name already taken",
            "content": {"application/json":{"example": {"detail": HttpError[lang]['products.name_taken']['message']}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Item sub-category, Brand, Ticket variant & wholesale not found",
            "content": {"application/json": {"example": {"detail":"string"}}}
        },
        409: {
            "description": "Conflict",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['multiple_image.not_unique']['message']}}}
        },
        413: {
            "description": "Request Entity Too Large",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['single_image.not_lt']['message']}}}
        }
    }
)
async def create_product(form_data: create_form_product = Depends(), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    form_data['slug'] = slugify(form_data['name'])

    # check name duplicate
    if await ProductFetch.filter_by_slug(form_data['slug']):
        raise HTTPException(status_code=400,detail=HttpError[lang]['products.name_taken'])
    # check item_sub_category_id exists in db
    if not await ItemSubCategoryFetch.filter_by_id(form_data['item_sub_category_id']):
        raise HTTPException(status_code=404,detail=HttpError[lang]['products.item_sub_category_not_found'])
    # check brand exists in db if data supplied
    if form_data['brand_id'] and not await BrandFetch.filter_by_id(form_data['brand_id']):
        raise HTTPException(status_code=404,detail=HttpError[lang]['products.brand_not_found'])

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
        index:value for index, value in form_data.items()
        if index != 'variant_data' and index != 'wholesale_data' and index != 'image_variant'
    }
    product_id = await ProductCrud.create_product(**product_data)

    # save variant to db
    variant_db = VariantLogic.convert_data_to_db(form_data['variant_data'],product_id)
    await VariantCrud.create_variant(variant_db)
    # save wholesale to db if exists
    if wholesale_data := form_data['wholesale_data']:
        [data.__setitem__('product_id',product_id) for data in wholesale_data]
        await WholeSaleCrud.create_wholesale(wholesale_data)

    return ResponseMessages[lang]['create_product'][201]

@router.get('/all-products',response_model=ProductPaginate)
async def get_all_products(query_string: get_all_query_product = Depends(), authorize: AuthJWT = Depends()):
    authorize.jwt_optional()

    results = await ProductFetch.get_all_products_paginate(**query_string)
    if user_id := int(authorize.get_jwt_subject() or 0):
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
            "content": {"application/json":{"example": ResponseMessages[lang]['change_product_alive_archive'][200]}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Product not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['products.not_found']['message']}}}
        }
    }
)
async def change_product_alive_archive(product_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if product := await ProductFetch.filter_by_id(product_id):
        await ProductCrud.change_product_alive_archive(product['id'],product['live'])
        msg = 'alive' if not product['live'] else 'archive'
        response = ResponseMessages[lang]['change_product_alive_archive'][200].copy()
        response.update({'ctx': {'msg': msg}})
        return response
    raise HTTPException(status_code=404,detail=HttpError[lang]['products.not_found'])

@router.get('/search-by-name',response_model=List[ProductSearchByName])
async def search_products_by_name(q: str = Query(...,min_length=1), limit: int = Query(...,gt=0)):
    return await ProductFetch.search_products_by_name(q=q,limit=limit)

@router.get('/{slug}',
    response_model=ProductDataSlug,
    response_model_exclude_none=True,
    responses={
        404: {
            "description": "Product not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['products.not_found']['message']}}}
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

    if product_data := await ProductFetch.filter_by_slug(slug):
        results = await ProductFetch.get_product_by_slug(product_data['slug'])

        if recommendation is True:
            redis = request.app.state.redis  # set redis conn from state
            await visitor.increment_visitor(table=product,id_=product_data['id'])  # set visitor

            # get product recommendation
            if redis.get(f"products_recommendation:{slug}") is None:
                results['products_recommendation'] = await ProductFetch.get_product_recommendation(limit=6)
                redis.set(
                    f"products_recommendation:{slug}",
                    json.dumps(results['products_recommendation'],default=str), 600
                )  # save product recommendation by slug in cache 10 minutes
            else:
                results['products_recommendation'] = json.loads(redis.get(f"products_recommendation:{slug}"))

        # check wishlist product & product recommendation
        if recommendation is True:
            if user_id := int(authorize.get_jwt_subject() or 0):
                results.__setitem__('products_love', await WishlistLogic.check_wishlist(product_data['id'],user_id))
                [
                    data.__setitem__('products_love',await WishlistLogic.check_wishlist(data['products_id'],user_id))
                    for data in results['products_recommendation']
                ]
            else:
                results.__setitem__('products_love', False)
                [data.__setitem__('products_love',False) for data in results['products_recommendation']]

        return results
    raise HTTPException(status_code=404,detail=HttpError[lang]['products.not_found'])

@router.put('/update/{product_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['update_product'][200]}}
        },
        400: {
            "description": "Name already taken",
            "content": {"application/json":{"example": {"detail": HttpError[lang]['products.name_taken']['message']}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example":{"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Product, Item sub-category, Brand, Ticket variant & wholesale not found",
            "content": {"application/json": {"example": {"detail":"string"}}}
        },
        409: {
            "description": "Conflict",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['multiple_image.not_unique']['message']}}}
        },
        413: {
            "description": "Request Entity Too Large",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['single_image.not_lt']['message']}}}
        }
    }
)
async def update_product(
    product_id: int = Path(...,gt=0),
    form_data: update_form_product = Depends(),
    authorize: AuthJWT = Depends()
):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if product := await ProductFetch.filter_by_id(product_id):
        form_data['slug'] = slugify(form_data['name'])
        # check name duplicate
        if product['slug'] != form_data['slug'] and await ProductFetch.filter_by_slug(form_data['slug']):
            raise HTTPException(status_code=400,detail=HttpError[lang]['products.name_taken'])
        # check item_sub_category_id exists in db
        if not await ItemSubCategoryFetch.filter_by_id(form_data['item_sub_category_id']):
            raise HTTPException(status_code=404,detail=HttpError[lang]['products.item_sub_category_not_found'])
        # check brand exists in db if data supplied
        if form_data['brand_id'] and not await BrandFetch.filter_by_id(form_data['brand_id']):
            raise HTTPException(status_code=404,detail=HttpError[lang]['products.brand_not_found'])

        # validate image on input variant
        image_variant_db = await VariantFetch.get_product_variant_image(product['id'])
        image_variant_input = [
            item.get('va1_image') for item in form_data['variant_data']['va1_items'] if item.get('va1_image')
        ]
        if True in [c not in image_variant_db for c in image_variant_input]:
            raise HTTPException(status_code=422,detail=HttpError[lang]['products.image_variant_not_found_in_db'])

        # validate image on input delete_size_guide is same with db
        if image_size_guide_delete := form_data['image_size_guide_delete']:
            if image_size_guide_delete != product['image_size_guide']:
                raise HTTPException(status_code=422,detail=HttpError[lang]['products.image_size_guide_delete_not_same_with_db'])

        # ================ IMAGE PRODUCT SECTION ================
        image_product_db = [item for item in json.loads(product['image_product']).values()]
        # delete image_product on db temporary
        if image_product_delete := form_data['image_product_delete']:
            for item in image_product_delete:
                try: image_product_db.remove(item)
                except ValueError: pass

            if len(image_product_db + (form_data.get('image_product') or [])) < 1:
                raise HTTPException(
                    status_code=422,
                    detail=HttpError[lang]['products.image_product_not_gt']
                )

        if image_product := form_data['image_product']:
            if len(image_product_db + image_product) > 10:
                raise HTTPException(status_code=422,detail=HttpError[lang]['products.image_product_max_items'])
            image_magic_products = MagicImage(
                square=True,
                file=image_product,
                width=550,
                height=550,
                path_upload='products/',
                dir_name=form_data['slug']
            )
            image_magic_products.save_image()
            image_magic_products = [item for item in image_magic_products.file_name.values()]
            image_product_db = [*image_product_db,*image_magic_products]

        # delete image_product on storage
        if image_product_delete := form_data['image_product_delete']:
            [
                MagicImage.delete_image(file=file,path_delete=f"products/{product['slug']}")
                for file in image_product_delete
            ]

        form_data['image_product'] = json.dumps({key:value for key,value in enumerate(image_product_db)})
        # ================ IMAGE PRODUCT SECTION ================

        # ================ IMAGE VARIANT SECTION ================
        # detect image to remove from storage
        if image_variant_remove := [item for item in image_variant_db if item not in image_variant_input]:
            [
                MagicImage.delete_image(file=file,path_delete=f"products/{product['slug']}")
                for file in image_variant_remove
            ]
        # save image to storage
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

            index_img = 0
            for item in form_data['variant_data']['va1_items']:
                if 'va1_image' not in item:
                    item.update({'va1_image': form_data['image_variant'][index_img]})
                    index_img += 1
        # ================ IMAGE VARIANT SECTION ================

        # ================ IMAGE SIZE GUIDE SECTION ================
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

        # delete image
        if image_size_guide_delete := form_data['image_size_guide_delete']:
            MagicImage.delete_image(file=image_size_guide_delete,path_delete=f"products/{product['slug']}")

        # pop image_size_guide from form_data if nothing happen
        if form_data['image_size_guide_delete'] is None and form_data['image_size_guide'] is None:
            form_data.pop('image_size_guide',None)
        # ================ IMAGE SIZE GUIDE SECTION ================

        # change folder name if name in db not same with form_data
        if product['slug'] != form_data['slug']:
            MagicImage.rename_folder(old_name=product['slug'],new_name=form_data['slug'],path_update='products/')

        # update product on db
        product_update_data = {
            key:value for key,value in form_data.items()
            if key != 'image_product_delete' and key != 'image_size_guide_delete' and
            key != 'image_variant' and key != 'variant_data' and key != 'wholesale_data'
        }
        await ProductCrud.update_product(product['id'],**product_update_data)

        # save variant to db
        variant_db = VariantLogic.convert_data_to_db(form_data['variant_data'],product['id'])
        variant_db_id = await VariantFetch.get_produt_variant_id(product['id'])
        # insert variant to db
        if variant_insert_data := [{i:v for i,v in x.items() if i not in ['id']} for x in variant_db if x['id'] == 0]:
            await VariantCrud.create_variant(variant_insert_data)
        # update variant to db
        if variant_update_data := [
            {i:v for i,v in x.items() if i not in ['discount','discount_active']} for x in variant_db if x['id'] > 0 and x['id'] in variant_db_id
        ]:
            await VariantCrud.update_variant(variant_update_data)
        # delete variant to db
        if variant_delete_id := [i for i in variant_db_id if i not in [x['id'] for x in variant_db if x['id'] > 0]]:
            await VariantCrud.delete_variant_by_id(variant_delete_id)

        # update wholesale if wholesale_data exists
        previous_wholesale = await WholeSaleFetch.get_wholesale_by_product_id(product['id'],exclude=['id','product_id'])
        if wholesale_data := form_data['wholesale_data']:
            # delete and create again wholesale if incoming data not same with db
            if previous_wholesale != wholesale_data:
                [data.__setitem__('product_id',product['id']) for data in wholesale_data]
                await WholeSaleCrud.delete_wholesale(product['id'])
                await WholeSaleCrud.create_wholesale(wholesale_data)

        # delete wholesale if in db exists and doesn't have ticket
        if previous_wholesale and form_data['wholesale_data'] is None:
            await WholeSaleCrud.delete_wholesale(product['id'])

        return ResponseMessages[lang]['update_product'][200]
    raise HTTPException(status_code=404,detail=HttpError[lang]['products.not_found'])

@router.delete('/delete/{product_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['delete_product'][200]}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example":{"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Product not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['products.not_found']['message']}}}
        }
    }
)
async def delete_product(product_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if product := await ProductFetch.filter_by_id(product_id):
        await ProductCrud.delete_product(product['id'])
        MagicImage.delete_folder(name_folder=product['slug'],path_delete='products/')
        return ResponseMessages[lang]['delete_product'][200]
    raise HTTPException(status_code=404,detail=HttpError[lang]['products.not_found'])
