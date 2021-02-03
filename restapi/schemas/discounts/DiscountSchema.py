import json
from pydantic import BaseModel, conint, constr, validator
from datetime import datetime, timedelta
from typing import List, Literal, Optional
from pytz import timezone
from config import settings

tz = timezone(settings.timezone)
tf = '%d %b %Y %H:%M'

class DiscountSchema(BaseModel):
    class Config:
        min_anystr_length = 1
        max_anystr_length = 100
        anystr_strip_whitespace = True

class DiscountCreate(DiscountSchema):
    product_id: conint(strict=True, gt=0)
    ticket_variant: constr(strict=True)
    discount_start: datetime
    discount_end: datetime

    class Config:
        schema_extra = {
            "example": {
                "product_id": 1,
                "ticket_variant": "string",
                "discount_start": format(datetime.now(tz) + timedelta(minutes=20), tf),
                "discount_end": format(datetime.now(tz) + timedelta(hours=1,minutes=20), tf)
            }
        }

    @validator('discount_start', 'discount_end', pre=True)
    def parse_discount_format(cls, v):
        return tz.localize(datetime.strptime(v,tf))

    @validator('discount_start')
    def validate_discount_start(cls, v):
        if datetime.now(tz) > v:
            raise ValueError("the start time must be after the current time")
        return v

    @validator('discount_end')
    def validate_discount_end(cls, v, values, **kwargs):
        if 'discount_start' in values:
            discount_between = (v - values['discount_start'])
            if (round(discount_between.seconds / 3600, 2) < 1 and discount_between.days < 1) or datetime.now(tz) > v:
                raise ValueError("the expiration time must be at least one hour longer than the start time")
            if discount_between.days > 180:
                raise ValueError("promo period must be less than 180 days")
        return v

class DiscountUpdate(DiscountSchema):
    product_id: conint(strict=True, gt=0)
    ticket_variant: constr(strict=True)
    discount_start: datetime
    discount_end: datetime

    class Config:
        schema_extra = {
            "example": {
                "product_id": 1,
                "ticket_variant": "string",
                "discount_start": format(datetime.now(tz) + timedelta(minutes=20), tf),
                "discount_end": format(datetime.now(tz) + timedelta(hours=1,minutes=20), tf)
            }
        }

    @validator('discount_start', 'discount_end', pre=True)
    def parse_discount_format(cls, v):
        return tz.localize(datetime.strptime(v,tf))

class DiscountData(DiscountSchema):
    products_id: int
    products_name: str
    products_slug: str
    products_image_product: str
    products_discount_start: Optional[datetime]
    products_discount_end: Optional[datetime]
    products_discount_status: Literal['ongoing','will_come','not_active','have_ended']

    variants_min_price: int
    variants_max_price: int
    variants_discount: int

    @validator('products_image_product',pre=True)
    def convert_image_product(cls, v):
        return json.loads(v)['0']

class DiscountPaginate(BaseModel):
    data: List[DiscountData]
    total: int
    next_num: Optional[int]
    prev_num: Optional[int]
    page: int
    iter_pages: list

# ============ DISCOUNT BY PRODUCT_ID ============

class DiscountVariantTwo(DiscountSchema):
    va2_id: int
    va2_option: str
    va2_price: int
    va2_stock: int
    va2_code: Optional[str]
    va2_barcode: Optional[str]
    va2_discount: Optional[int]
    va2_discount_active: Optional[bool]

class DiscountVariantOne(DiscountSchema):
    va1_id: Optional[int]
    va1_option: Optional[str]
    va1_price: Optional[int]
    va1_stock: Optional[int]
    va1_code: Optional[str]
    va1_barcode: Optional[str]
    va1_discount: Optional[int]
    va1_discount_active: Optional[bool]
    va1_image: Optional[str]
    va2_items: Optional[List[DiscountVariantTwo]]

class DiscountVariant(DiscountSchema):
    va1_name: Optional[str]
    va2_name: Optional[str]
    va1_items: List[DiscountVariantOne]

class DiscountDataProduct(DiscountSchema):
    products_name: str
    products_discount_start: Optional[datetime]
    products_discount_end: Optional[datetime]
    products_variant: DiscountVariant

# ============ DISCOUNT BY PRODUCT_ID ============
