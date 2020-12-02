import json
from fastapi import UploadFile, File, Form, Depends, HTTPException
from libs.MagicImage import validate_multiple_upload_images, validate_single_upload_image
from typing import Optional, List
from config import redis_conn

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

def upload_image_size_guide_product(image_size_guide_product: Optional[UploadFile] = File(None)):
    if not image_size_guide_product: return

    return validate_single_upload_image(
        image=image_size_guide_product,
        allow_file_ext=['jpg','png','jpeg'],
        max_file_size=4
    )

def create_form_product(
    name_product: str = Form(...,min_length=5,max_length=100),
    desc_product: str = Form(...,min_length=20),
    condition_product: bool = Form(...),
    weight_product: int = Form(...,gt=0),
    video_product: str = Form(None,min_length=2,regex=r"^(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.+"),
    preorder_product: int = Form(None,gt=0,le=500),
    ticket_variant: str = Form(...,min_length=5,max_length=100),
    item_sub_category_id: int = Form(...,gt=0),
    brand_id: int = Form(None,gt=0),
    image_product: upload_image_product = Depends(),
    image_variant: upload_image_variant = Depends(),
    image_size_guide_product: upload_image_size_guide_product = Depends()
):

    if variant_data := redis_conn.get(ticket_variant):
        variant_data = json.loads(variant_data)
        # match variant_data with image without, single and double variant
        if 'va1_name' not in variant_data and image_variant:
            raise HTTPException(status_code=422,detail="The image must not be filled.")

        # without image or all image must be filled if single or double variant
        len_va1_items = len(variant_data['va1_items'])
        len_image_variant = len(image_variant or [])
        if len_image_variant != 0 and len_image_variant != len_va1_items:
            raise HTTPException(status_code=422,detail="You must fill all image or even without image.")
    else:
        raise HTTPException(status_code=404,detail="Ticket variant not found!")

    return {
        "name_product": name_product,
        "desc_product": desc_product,
        "condition_product": condition_product,
        "weight_product": weight_product,
        "video_product": video_product,
        "preorder_product": preorder_product,
        "item_sub_category_id": item_sub_category_id,
        "brand_id": brand_id,
        "image_product": image_product,
        "image_size_guide_product": image_size_guide_product,
        "variant_data": variant_data,
        "image_variant": image_variant
    }
