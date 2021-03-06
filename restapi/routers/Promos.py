from fastapi import APIRouter, Query, Path, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from controllers.PromoController import PromoFetch, PromoCrud
from controllers.UserController import UserFetch
from dependencies.PromoDependant import create_form_promo
from libs.MagicImage import MagicImage
from localization import LocalizationRoute
from I18N import HttpError, ResponseMessages
from config import settings
from slugify import slugify

router = APIRouter(route_class=LocalizationRoute)
# default language response
lang = settings.default_language_code

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

@router.get('/all-promos')
async def get_all_promos():
    pass

@router.get('/search-by-name')
async def search_promos_by_name(q: str = Query(...,min_length=1), limit: int = Query(...,gt=0)):
    pass

@router.get('/{slug}')
async def get_promos_by_slug(slug: str = Path(...,min_length=1)):
    pass

@router.put('/update/{promo_id}')
async def update_promo(promo_id: int = Path(...,gt=0)):
    pass

@router.delete('/delete/{promo_id}')
async def deete_promo(promo_id: int = Path(...,gt=0)):
    pass
