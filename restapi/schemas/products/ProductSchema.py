import json
from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional, List

class ProductSchema(BaseModel):
    class Config:
        anystr_strip_whitespace = True

class ProductData(ProductSchema):
    products_id: int
    products_name: str
    products_slug: str
    products_image_product: str
    products_live: bool
    products_love: bool
    products_wholesale: bool
    products_created_at: str
    products_updated_at: str

    variants_price: int

    @validator('products_image_product',pre=True)
    def convert_image_product(cls, v):
        return json.loads(v)['0']

    @validator('products_created_at','products_updated_at',pre=True)
    def convert_datetime_to_str(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v

class ProductPaginate(BaseModel):
    data: List[ProductData]
    total: int
    next_num: Optional[int]
    prev_num: Optional[int]
    page: int
    iter_pages: list

# ============ PRODUCT SLUG ============

class ProductWholeSale(ProductSchema):
    wholesale_id: int
    wholesale_min_qty: int
    wholesale_price: int

class ProductCategory(ProductSchema):
    categories_id: int
    categories_name: str
    sub_categories_id: int
    sub_categories_name: str
    item_sub_categories_id: int
    item_sub_categories_name: str

class ProductBrand(ProductSchema):
    brands_id: Optional[int]
    brands_name: Optional[str]
    brands_image: Optional[str]

class ProductVariantTwo(ProductSchema):
    va2_id: int
    va2_option: str
    va2_price: int
    va2_stock: int
    va2_code: Optional[str]
    va2_barcode: Optional[str]

class ProductVariantOne(ProductSchema):
    va1_id: Optional[int]
    va1_option: Optional[str]
    va1_price: Optional[int]
    va1_stock: Optional[int]
    va1_code: Optional[str]
    va1_barcode: Optional[str]
    va1_image: Optional[str]
    va2_items: Optional[List[ProductVariantTwo]]

class ProductVariant(ProductSchema):
    va1_name: Optional[str]
    va2_name: Optional[str]
    va1_items: List[ProductVariantOne]

class ProductDataSlug(ProductSchema):
    products_id: int
    products_name: str
    products_slug: str
    products_desc: str
    products_condition: bool
    products_image_product: dict
    products_weight: int
    products_image_size_guide: Optional[str]
    products_video: Optional[str]
    products_preorder: Optional[int]
    products_live: bool
    products_visitor: int
    products_love: Optional[bool]
    products_category: ProductCategory
    products_brand: Optional[ProductBrand]
    products_variant: ProductVariant
    products_wholesale: Optional[List[ProductWholeSale]]
    products_recommendation: Optional[List[ProductData]]

    products_created_at: str
    products_updated_at: str

    @validator('products_image_product',pre=True)
    def convert_image_product(cls, v):
        return json.loads(v)

    @validator('products_created_at','products_updated_at',pre=True)
    def convert_datetime_to_str(cls, v):
        return v.isoformat()

# ============ PRODUCT SLUG ============

class ProductSearchByName(ProductSchema):
    value: str

    @validator('value',pre=True)
    def convert_to_lowercase(cls, v):
        return v.lower()
