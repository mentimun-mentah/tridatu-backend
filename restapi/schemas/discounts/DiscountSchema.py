import json
from pydantic import BaseModel, constr, validator
from datetime import datetime, timedelta
from typing import List, Literal, Optional
from pytz import timezone
from config import settings
from schemas import errors

tz = timezone(settings.timezone)
tf = '%d %b %Y %H:%M'

class DiscountSchema(BaseModel):
    class Config:
        min_anystr_length = 1
        anystr_strip_whitespace = True

class DiscountCreate(DiscountSchema):
    product_id: constr(strict=True, regex=r'^[0-9]*$')
    ticket_variant: constr(strict=True, max_length=100)
    discount_start: datetime
    discount_end: datetime

    class Config:
        schema_extra = {
            "example": {
                "product_id": "1",
                "ticket_variant": "string",
                "discount_start": format(datetime.now(tz) + timedelta(minutes=20), tf),
                "discount_end": format(datetime.now(tz) + timedelta(hours=1,minutes=20), tf)
            }
        }

    @validator('product_id')
    def parse_str_to_int(cls, v):
        return int(v) if v else None

    @validator('discount_start', 'discount_end', pre=True)
    def parse_discount_format(cls, v):
        return tz.localize(datetime.strptime(v,tf))

    @validator('discount_start')
    def validate_discount_start(cls, v):
        if datetime.now(tz) > v:
            raise errors.DiscountStartTimeError()
        return v

    @validator('discount_end')
    def validate_discount_end(cls, v, values, **kwargs):
        if 'discount_start' in values:
            discount_between = (v - values['discount_start'])
            if (round(discount_between.seconds / 3600, 2) < 1 and discount_between.days < 1) or datetime.now(tz) > v:
                raise errors.DiscountEndMinExpError()
            if discount_between.days > 180:
                raise errors.DiscountEndMaxExpError()
        return v

class DiscountUpdate(DiscountSchema):
    product_id: constr(strict=True, regex=r'^[0-9]*$')
    ticket_variant: constr(strict=True, max_length=100)
    discount_start: datetime
    discount_end: datetime

    class Config:
        schema_extra = {
            "example": {
                "product_id": "1",
                "ticket_variant": "string",
                "discount_start": format(datetime.now(tz) + timedelta(minutes=20), tf),
                "discount_end": format(datetime.now(tz) + timedelta(hours=1,minutes=20), tf)
            }
        }

    @validator('product_id')
    def parse_str_to_int(cls, v):
        return int(v) if v else None

    @validator('discount_start', 'discount_end', pre=True)
    def parse_discount_format(cls, v):
        return tz.localize(datetime.strptime(v,tf))

class DiscountData(DiscountSchema):
    products_id: str
    products_name: str
    products_slug: str
    products_image_product: str
    products_discount_start: Optional[datetime]
    products_discount_end: Optional[datetime]
    products_discount_status: Literal['ongoing','will_come','not_active','have_ended']

    variants_min_price: str
    variants_max_price: str
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
    va2_id: str
    va2_option: str
    va2_price: str
    va2_stock: str
    va2_code: Optional[str]
    va2_barcode: Optional[str]
    va2_discount: Optional[int]
    va2_discount_active: Optional[bool]

class DiscountVariantOne(DiscountSchema):
    va1_id: Optional[str]
    va1_option: Optional[str]
    va1_price: Optional[str]
    va1_stock: Optional[str]
    va1_code: Optional[str]
    va1_barcode: Optional[str]
    va1_discount: Optional[int]
    va1_discount_active: Optional[bool]
    va1_image: Optional[str]
    va2_items: Optional[List[DiscountVariantTwo]]

class DiscountVariant(DiscountSchema):
    va1_name: Optional[str]
    va2_name: Optional[str]
    va1_product_id: Optional[str]
    va1_items: List[DiscountVariantOne]

class DiscountDataProduct(DiscountSchema):
    products_name: str
    products_discount_start: Optional[datetime]
    products_discount_end: Optional[datetime]
    products_variant: DiscountVariant

# ============ DISCOUNT BY PRODUCT_ID ============
