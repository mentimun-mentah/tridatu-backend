from fastapi import UploadFile, File, Form, Depends, HTTPException
from libs.MagicImage import validate_single_upload_image
from datetime import datetime, timedelta
from pytz import timezone
from config import settings
from I18N import HttpError
from typing import Optional

tz = timezone(settings.timezone)
tf = '%d %b %Y %H:%M'

# default language response
lang = settings.default_language_code

def upload_image_promo(image: Optional[UploadFile] = File(None)):
    if not image: return

    return validate_single_upload_image(
        image=image,
        allow_file_ext=['jpg','png','jpeg'],
        max_file_size=4
    )

def create_form_promo(
    name: str = Form(...,min_length=5,max_length=100),
    desc: str = Form(None,min_length=5),
    terms_condition: str = Form(None,min_length=5),
    seen: bool = Form(...),
    period_start: str = Form(...,description=format(datetime.now(tz) + timedelta(minutes=20), tf)),
    period_end: str = Form(...,description=format(datetime.now(tz) + timedelta(days=1,minutes=20), tf)),
    image: upload_image_promo = Depends(),
):

    if seen is True and desc is None:
        raise HTTPException(status_code=422,detail=HttpError[lang]['promos.desc_missing'])
    if seen is True and terms_condition is None:
        raise HTTPException(status_code=422,detail=HttpError[lang]['promos.terms_condition_missing'])
    if seen is True and image is None:
        raise HTTPException(status_code=422,detail=HttpError[lang]['promos.image_missing'])

    # set desc, terms_condition, image to none if seen is False
    if seen is False:
        desc, terms_condition, image = None, None, None

    try:
        period_start = tz.localize(datetime.strptime(period_start,tf))
    except ValueError:
        msg = HttpError[lang]['promos.datetime_zone_format']
        msg['ctx'].update({'input_user': period_start, 'tf': tf})
        raise HTTPException(status_code=422,detail=msg)

    try:
        period_end = tz.localize(datetime.strptime(period_end,tf))
    except ValueError:
        msg = HttpError[lang]['promos.datetime_zone_format']
        msg['ctx'].update({'input_user': period_end, 'tf': tf})
        raise HTTPException(status_code=422,detail=msg)

    period_between = (period_end - period_start)

    if datetime.now(tz) > period_start:
        raise HTTPException(status_code=422,detail=HttpError[lang]['promos.start_time_create'])
    if period_between.days < 1 or datetime.now(tz) > period_end:
        raise HTTPException(status_code=422,detail=HttpError[lang]['promos.min_exp'])
    if period_between.days > 180:
        raise HTTPException(status_code=422,detail=HttpError[lang]['promos.max_exp'])

    return {
        "name": name,
        "desc": desc,
        "terms_condition": terms_condition,
        "seen": seen,
        "period_start": period_start,
        "period_end": period_end,
        "image": image
    }

def update_form_promo(
    name: str = Form(...,min_length=5,max_length=100),
    desc: str = Form(None,min_length=5),
    terms_condition: str = Form(None,min_length=5),
    seen: bool = Form(...),
    period_start: str = Form(...,description=format(datetime.now(tz) + timedelta(minutes=20), tf)),
    period_end: str = Form(...,description=format(datetime.now(tz) + timedelta(days=1,minutes=20), tf)),
    image: upload_image_promo = Depends(),
):

    if seen is True and desc is None:
        raise HTTPException(status_code=422,detail=HttpError[lang]['promos.desc_missing'])
    if seen is True and terms_condition is None:
        raise HTTPException(status_code=422,detail=HttpError[lang]['promos.terms_condition_missing'])

    # set desc, terms_condition, image to none if seen is False
    if seen is False:
        desc, terms_condition, image = None, None, None

    try:
        period_start = tz.localize(datetime.strptime(period_start,tf))
    except ValueError:
        msg = HttpError[lang]['promos.datetime_zone_format']
        msg['ctx'].update({'input_user': period_start, 'tf': tf})
        raise HTTPException(status_code=422,detail=msg)

    try:
        period_end = tz.localize(datetime.strptime(period_end,tf))
    except ValueError:
        msg = HttpError[lang]['promos.datetime_zone_format']
        msg['ctx'].update({'input_user': period_end, 'tf': tf})
        raise HTTPException(status_code=422,detail=msg)

    return {
        "name": name,
        "desc": desc,
        "terms_condition": terms_condition,
        "seen": seen,
        "period_start": period_start,
        "period_end": period_end,
        "image": image
    }
