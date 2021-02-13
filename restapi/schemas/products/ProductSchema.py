import json
from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional, List, Literal

class ProductSchema(BaseModel):
    class Config:
        anystr_strip_whitespace = True

class ProductData(ProductSchema):
    products_id: str
    products_name: str
    products_slug: str
    products_image_product: str
    products_live: bool
    products_love: bool
    products_wholesale: bool
    products_discount_status: Literal['ongoing','will_come','not_active','have_ended']
    products_created_at: datetime
    products_updated_at: datetime

    variants_min_price: str
    variants_max_price: str
    variants_discount: int

    @validator('products_image_product',pre=True)
    def convert_image_product(cls, v):
        return json.loads(v)['0']

class ProductPaginate(BaseModel):
    data: List[ProductData]
    total: int
    next_num: Optional[int]
    prev_num: Optional[int]
    page: int
    iter_pages: list

# ============ PRODUCT SLUG ============

class ProductWholeSale(ProductSchema):
    wholesale_id: str
    wholesale_min_qty: int
    wholesale_price: str

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
    va2_id: str
    va2_option: str
    va2_price: str
    va2_stock: str
    va2_code: Optional[str]
    va2_barcode: Optional[str]
    va2_discount: Optional[int]
    va2_discount_active: Optional[bool]

class ProductVariantOne(ProductSchema):
    va1_id: Optional[str]
    va1_option: Optional[str]
    va1_price: Optional[str]
    va1_stock: Optional[str]
    va1_code: Optional[str]
    va1_barcode: Optional[str]
    va1_discount: Optional[int]
    va1_discount_active: Optional[bool]
    va1_image: Optional[str]
    va2_items: Optional[List[ProductVariantTwo]]

class ProductVariant(ProductSchema):
    va1_name: Optional[str]
    va2_name: Optional[str]
    va1_product_id: Optional[str]
    va1_items: List[ProductVariantOne]

class ProductDataSlug(ProductSchema):
    products_id: str
    products_name: str
    products_slug: str
    products_desc: str
    products_condition: bool
    products_image_product: dict
    products_weight: str
    products_image_size_guide: Optional[str]
    products_video: Optional[str]
    products_preorder: Optional[int]
    products_live: bool
    products_visitor: str
    products_love: Optional[bool]
    products_category: ProductCategory
    products_brand: Optional[ProductBrand]
    products_variant: ProductVariant
    products_wholesale: Optional[List[ProductWholeSale]]
    products_recommendation: Optional[List[ProductData]]

    products_created_at: datetime
    products_updated_at: datetime
    products_discount_status: Literal['ongoing','will_come','not_active','have_ended']

    variants_min_price: str
    variants_max_price: str
    variants_discount: int

    @validator('products_image_product',pre=True)
    def convert_image_product(cls, v):
        return json.loads(v)

# ============ PRODUCT SLUG ============

class ProductSearchByName(ProductSchema):
    value: str

    @validator('value',pre=True)
    def convert_to_lowercase(cls, v):
        return v.lower()
