import json
from fastapi import UploadFile, File, Form, Query, Depends, HTTPException
from libs.MagicImage import validate_multiple_upload_images, validate_single_upload_image
from typing import Optional, List, Literal
from config import redis_conn

def parse_int_list(items: List[str], seperator: str) -> List[int]:
    try:
        return [int(float(item)) for item in items.split(seperator)]
    except Exception:
        return None

def upload_image_product(image_product: List[UploadFile] = File(...)):
    return validate_multiple_upload_images(
        images=image_product,
        allow_file_ext=['jpg','png','jpeg'],
        max_file_size=4,
        max_file_in_list=10
    )

def upload_image_variant(image_variant: Optional[List[UploadFile]] = File(None)):
    if not image_variant: return

    return validate_multiple_upload_images(
        images=image_variant,
        allow_file_ext=['jpg','png','jpeg'],
        max_file_size=4,
        max_file_in_list=20
    )

def upload_image_size_guide(image_size_guide: Optional[UploadFile] = File(None)):
    if not image_size_guide: return

    return validate_single_upload_image(
        image=image_size_guide,
        allow_file_ext=['jpg','png','jpeg'],
        max_file_size=4
    )

def create_form_product(
    name: str = Form(...,min_length=5,max_length=100),
    desc: str = Form(...,min_length=20),
    condition: bool = Form(...),
    weight: int = Form(...,gt=0),
    video: str = Form(None,min_length=2,regex=r"^(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.+"),
    preorder: int = Form(None,gt=0,le=500),
    ticket_variant: str = Form(...,min_length=5,max_length=100),
    item_sub_category_id: int = Form(...,gt=0),
    brand_id: int = Form(None,gt=0),
    image_product: upload_image_product = Depends(),
    image_variant: upload_image_variant = Depends(),
    image_size_guide: upload_image_size_guide = Depends()
):

    if variant_data := redis_conn.get(ticket_variant):
        variant_data = json.loads(variant_data)
        # match variant_data with image without, single and double variant
        if 'va1_name' not in variant_data and image_variant:
            raise HTTPException(status_code=422,detail="The image variant must not be filled.")

        # without image or all image must be filled if single or double variant
        len_va1_items = len(variant_data['va1_items'])
        len_image_variant = len(image_variant or [])
        if len_image_variant != 0 and len_image_variant != len_va1_items:
            raise HTTPException(status_code=422,detail="You must fill all variant images or even without images.")
    else:
        raise HTTPException(status_code=404,detail="Ticket variant not found!")

    return {
        "name": name,
        "desc": desc,
        "condition": condition,
        "weight": weight,
        "video": video,
        "preorder": preorder,
        "item_sub_category_id": item_sub_category_id,
        "brand_id": brand_id,
        "image_product": image_product,
        "image_variant": image_variant,
        "image_size_guide": image_size_guide,
        "variant_data": variant_data
    }

def get_all_query_product(
    page: int = Query(...,gt=0),
    per_page: int = Query(...,gt=0),
    q: str = Query(None,min_length=1),
    live: bool = Query(None),
    order_by: Literal['high_price','low_price','newest'] = Query(
        None, description="Example 'high_price', 'low_price', 'newest'"
    ),
    p_min: int = Query(None,gt=0),
    p_max: int = Query(None,gt=0),
    item_sub_cat: str = Query(None,min_length=1,description="Example 1,2,3"),
    brand: str = Query(None,min_length=1,description="Example 1,2,3"),
    pre_order: bool = Query(None),
    condition: bool = Query(None)
):
    return {
        "page": page,
        "per_page": per_page,
        "q": q,
        "live": live,
        "order_by": order_by,
        "p_min": p_min,
        "p_max": p_max,
        "item_sub_cat": parse_int_list(item_sub_cat,','),
        "brand": parse_int_list(brand,','),
        "pre_order": pre_order,
        "condition": condition
    }
