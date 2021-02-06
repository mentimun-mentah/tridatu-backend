import json
from fastapi import UploadFile, File, Form, Query, Depends, HTTPException
from libs.MagicImage import validate_multiple_upload_images, validate_single_upload_image
from libs.Parser import parse_int_list, parse_str_list
from typing import Optional, List, Literal
from config import redis_conn

def upload_image_product(image_product: List[UploadFile] = File(...)):
    return validate_multiple_upload_images(
        images=image_product,
        allow_file_ext=['jpg','png','jpeg'],
        max_file_size=4,
        max_file_in_list=10
    )

def upload_image_product_optional(image_product: Optional[List[UploadFile]] = File(None)):
    if not image_product: return

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
    ticket_wholesale: str = Form(None,min_length=5,max_length=100),
    item_sub_category_id: int = Form(...,gt=0),
    brand_id: int = Form(None,gt=0),
    image_product: upload_image_product = Depends(),
    image_variant: upload_image_variant = Depends(),
    image_size_guide: upload_image_size_guide = Depends()
):
    if variant_data := redis_conn.get(ticket_variant):
        variant_data = json.loads(variant_data)
        # image cannot be passed if no variant
        if 'va1_name' not in variant_data and image_variant:
            raise HTTPException(status_code=422,detail="The image variant must not be filled.")

        # without image or all image must be filled if single or double variant
        len_va1_items = len(variant_data['va1_items'])
        len_image_variant = len(image_variant or [])
        if len_image_variant != 0 and len_image_variant != len_va1_items:
            raise HTTPException(status_code=422,detail="You must fill all variant images or even without images.")
    else:
        raise HTTPException(status_code=404,detail="Ticket variant not found!")

    wholesale_data = None

    if ticket_wholesale and not redis_conn.get(ticket_wholesale):
        raise HTTPException(status_code=404,detail="Ticket wholesale not found!")
    if ticket_wholesale and redis_conn.get(ticket_wholesale):
        wholesale_data = json.loads(redis_conn.get(ticket_wholesale))['items']

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
        "variant_data": variant_data,
        "wholesale_data": wholesale_data
    }

def update_form_product(
    name: str = Form(...,min_length=5,max_length=100),
    desc: str = Form(...,min_length=20),
    condition: bool = Form(...),
    weight: int = Form(...,gt=0),
    video: str = Form(None,min_length=2,regex=r"^(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.+"),
    preorder: int = Form(None,gt=0,le=500),
    ticket_variant: str = Form(...,min_length=5,max_length=100),
    ticket_wholesale: str = Form(None,min_length=5,max_length=100),
    item_sub_category_id: int = Form(...,gt=0),
    brand_id: int = Form(None,gt=0),
    image_product_delete: str = Form(None,min_length=2,description="Example 1.jpg,2.png,3.jpeg"),
    image_size_guide_delete: str = Form(None,min_length=2,description="Example 1.jpg"),
    image_product: upload_image_product_optional = Depends(),
    image_variant: upload_image_variant = Depends(),
    image_size_guide: upload_image_size_guide = Depends()
):
    if variant_data := redis_conn.get(ticket_variant):
        variant_data = json.loads(variant_data)
        # image cannot be passed if no variant
        if 'va1_name' not in variant_data and image_variant:
            raise HTTPException(status_code=422,detail="The image variant must not be filled.")

        if 'va1_product_id' not in variant_data:
            raise HTTPException(status_code=422,detail="You must fill an id on variant product.")
        # without image or all image must be filled if single or double variant
        len_va1_image = len([x.get('va1_image') for x in variant_data['va1_items'] if x.get('va1_image')])
        len_va1_items = len(variant_data['va1_items'])
        len_image_variant = len(image_variant or [])
        if (len_va1_image + len_image_variant) != 0 and (len_va1_image + len_image_variant) != len_va1_items:
            raise HTTPException(status_code=422,detail="You must fill all variant images or even without images.")
    else:
        raise HTTPException(status_code=404,detail="Ticket variant not found!")

    image_product_delete = parse_str_list(image_product_delete,",")
    if image_product_delete and False in [img.endswith(('.jpg','.png','.jpeg')) for img in image_product_delete]:
        raise HTTPException(status_code=422,detail="Invalid image format on image_product_delete")

    if image_size_guide_delete and image_size_guide_delete.endswith(('.jpg','.png','.jpeg')) is False:
        raise HTTPException(status_code=422,detail="Invalid image format on image_size_guide_delete")

    wholesale_data = None

    if ticket_wholesale and not redis_conn.get(ticket_wholesale):
        raise HTTPException(status_code=404,detail="Ticket wholesale not found!")
    if ticket_wholesale and redis_conn.get(ticket_wholesale):
        wholesale_data = json.loads(redis_conn.get(ticket_wholesale))['items']

    return {
        "name": name,
        "desc": desc,
        "condition": condition,
        "weight": weight,
        "video": video,
        "preorder": preorder,
        "item_sub_category_id": item_sub_category_id,
        "brand_id": brand_id,
        "image_product_delete": image_product_delete,
        "image_size_guide_delete": image_size_guide_delete,
        "image_product": image_product,
        "image_variant": image_variant,
        "image_size_guide": image_size_guide,
        "variant_data": variant_data,
        "wholesale_data": wholesale_data
    }

def get_all_query_product(
    page: int = Query(...,gt=0),
    per_page: int = Query(...,gt=0),
    q: str = Query(None,min_length=1),
    live: bool = Query(None),
    order_by: Literal['high_price','low_price','newest','visitor'] = Query(
        None, description="Example 'high_price', 'low_price', 'newest', 'visitor'"
    ),
    p_min: int = Query(None,gt=0),
    p_max: int = Query(None,gt=0),
    item_sub_cat: str = Query(None,min_length=1,description="Example 1,2,3"),
    brand: str = Query(None,min_length=1,description="Example 1,2,3"),
    pre_order: bool = Query(None),
    condition: bool = Query(None),
    wholesale: bool = Query(None)
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
        "condition": condition,
        "wholesale": wholesale
    }
