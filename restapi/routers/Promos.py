from fastapi import APIRouter, Path, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from controllers.PromoController import PromoFetch, PromoCrud, PromoLogic
from controllers.UserController import UserFetch
from dependencies.PromoDependant import create_form_promo, update_form_promo
from libs.MagicImage import MagicImage
from localization import LocalizationRoute
from I18N import HttpError, ResponseMessages
from config import settings
from pytz import timezone
from slugify import slugify

router = APIRouter(route_class=LocalizationRoute)
# default language response
lang = settings.default_language_code

tz = timezone(settings.timezone)

@router.post('/create',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['create_promo'][201]}}
        },
        400: {
            "description": "Name already taken",
            "content": {"application/json":{"example": {"detail": HttpError[lang]['promos.name_taken']['message']}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        413: {
            "description": "Request Entity Too Large",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['single_image.not_lt']['message']}}}
        }
    }
)
async def create_promo(form_data: create_form_promo = Depends(), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    form_data['slug'] = slugify(form_data['name'])

    # check name duplicate
    if await PromoFetch.filter_by_slug(form_data['slug']):
        raise HTTPException(status_code=400,detail=HttpError[lang]['promos.name_taken'])

    # save image to promo folder if supplied
    if image := form_data['image']:
        image_magic = MagicImage(
            file=image.file,
            width=800,
            height=400,
            path_upload='promos/'
        )
        image_magic.save_image()
        form_data['image'] = image_magic.file_name

    # save promo to db
    form_data['period_start'] = form_data['period_start'].replace(tzinfo=None)
    form_data['period_end'] = form_data['period_end'].replace(tzinfo=None)
    await PromoCrud.create_promo(**form_data)

    return ResponseMessages[lang]['create_promo'][201]

# @router.get('/all-promos')
# async def get_all_promos():
#     pass

# @router.get('/search-by-name')
# async def search_promos_by_name(q: str = Query(...,min_length=1), limit: int = Query(...,gt=0)):
#     pass

# @router.get('/{slug}')
# async def get_promos_by_slug(slug: str = Path(...,min_length=1)):
#     pass

@router.put('/update/{promo_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['update_promo'][200]}}
        },
        400: {
            "description": "Name already taken",
            "content": {"application/json":{"example": {"detail": HttpError[lang]['promos.name_taken']['message']}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example":{"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Promo not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['promos.not_found']['message']}}}
        },
        413: {
            "description": "Request Entity Too Large",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['single_image.not_lt']['message']}}}
        }
    }
)
async def update_promo(
    promo_id: int = Path(...,gt=0),
    form_data: update_form_promo = Depends(),
    authorize: AuthJWT = Depends()
):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if promo := await PromoFetch.filter_by_id(promo_id):
        # image required if seen True and doesn't have image on db
        if form_data['seen'] is True and promo['image'] is None and form_data['image'] is None:
            raise HTTPException(status_code=422,detail=HttpError[lang]['promos.image_missing'])

        form_data['slug'] = slugify(form_data['name'])
        # check name duplicate
        if promo['slug'] != form_data['slug'] and await PromoFetch.filter_by_slug(form_data['slug']):
            raise HTTPException(status_code=400,detail=HttpError[lang]['promos.name_taken'])

        # validation period promo
        period_db = [{index:value for index,value in promo.items() if index in ['period_start','period_end']}]
        period_db = PromoLogic.set_period_status(period_db)[0]

        period_start = tz.localize(period_db['period_start'])
        # set input to data from db when promo is ongoing
        if period_db['period_status'] == 'ongoing':
            form_data['period_start'] = period_start

        period_between = (form_data['period_end'] - form_data['period_start'])

        if period_start > form_data['period_start']:
            raise HTTPException(status_code=422,detail=HttpError[lang]['promos.start_time_update'])
        if period_between.days < 1 or period_start > form_data['period_end']:
            raise HTTPException(status_code=422,detail=HttpError[lang]['promos.min_exp'])
        if period_between.days > 180:
            raise HTTPException(status_code=422,detail=HttpError[lang]['promos.max_exp'])

        # delete image
        if (promo['image'] and form_data['seen'] is False) or (form_data['image'] and promo['image']):
            MagicImage.delete_image(file=promo['image'],path_delete='promos/')

        # save image to promo folder if supplied
        if image := form_data['image']:
            image_magic = MagicImage(
                file=image.file,
                width=800,
                height=400,
                path_upload='promos/'
            )
            image_magic.save_image()
            form_data['image'] = image_magic.file_name

        # update data
        form_data['period_start'] = form_data['period_start'].replace(tzinfo=None)
        form_data['period_end'] = form_data['period_end'].replace(tzinfo=None)
        if form_data['image'] is None and form_data['seen'] is True:
            form_data.pop('image',None)

        await PromoCrud.update_promo(promo['id'],**form_data)

        return ResponseMessages[lang]['update_promo'][200]
    raise HTTPException(status_code=404,detail=HttpError[lang]['promos.not_found'])

@router.delete('/delete/{promo_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": ResponseMessages[lang]['delete_promo'][200]}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example":{"detail": HttpError[lang]['user_controller.not_admin']['message']}}}
        },
        404: {
            "description": "Promo not found",
            "content": {"application/json": {"example": {"detail": HttpError[lang]['promos.not_found']['message']}}}
        },
    }
)
async def delete_promo(promo_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    if promo := await PromoFetch.filter_by_id(promo_id):
        MagicImage.delete_image(file=promo['image'],path_delete='promos/')
        await PromoCrud.delete_promo(promo['id'])
        return ResponseMessages[lang]['delete_promo'][200]
    raise HTTPException(status_code=404,detail=HttpError[lang]['promos.not_found'])
