import json
from pydantic import BaseModel, validator
from typing import Optional, List

class ProductSchema(BaseModel):
    products_id: int
    products_name: str
    products_slug: str
    products_image_product: dict
    products_live: bool
    products_created_at: str
    products_updated_at: str

    @validator('products_image_product',pre=True)
    def convert_image_product(cls, v):
        return json.loads(v)

    @validator('products_created_at','products_updated_at',pre=True)
    def convert_datetime_to_str(cls, v):
        return v.isoformat()

    class Config:
        anystr_strip_whitespace = True

class ProductData(ProductSchema):
    variants_price: int

class ProductPaginate(BaseModel):
    data: List[ProductData]
    total: int
    next_num: Optional[int]
    prev_num: Optional[int]
    page: int
    iter_pages: list

class ProductSearchByName(BaseModel):
    value: str

    @validator('value',pre=True)
    def convert_to_lowercase(cls, v):
        return v.lower()

    class Config:
        anystr_strip_whitespace = True
