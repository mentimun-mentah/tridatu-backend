import json
from pydantic import BaseModel, validator
from typing import Optional, List

class ProductSchema(BaseModel):
    id_product: int
    name_product: str
    slug_product: str
    # desc_product: str
    # condition_product: bool
    image_product: dict
    # weight_product: int
    # image_size_guide_product: Optional[str]
    # video_product: Optional[str]
    # preorder_product: Optional[int]
    # live_product: bool
    # item_sub_category_id: int
    # brand_id: Optional[int]
    created_at: str
    updated_at: str

    @validator('image_product',pre=True)
    def convert_image_product(cls, v):
        return json.loads(v)

    @validator('created_at','updated_at',pre=True)
    def convert_datetime_to_str(cls, v):
        return v.isoformat()

class ProductData(ProductSchema):
    price_variant: int

class ProductPaginate(BaseModel):
    data: List[ProductData]
    total: int
    next_num: Optional[int]
    prev_num: Optional[int]
    page: int
    iter_pages: list
