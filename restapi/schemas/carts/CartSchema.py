import json
from pydantic import BaseModel, conint, constr, conlist, validator
from typing import Optional, Literal

class CartSchema(BaseModel):
    class Config:
        min_anystr_length = 1
        anystr_strip_whitespace = True

class CartCreateUpdate(CartSchema):
    variant_id: conint(strict=True, gt=0)
    qty: conint(strict=True, gt=0)
    operation: Literal['update','create']
    note: Optional[constr(strict=True, max_length=100)]

class CartDelete(CartSchema):
    cartIds: conlist(str, min_items=1, max_items=20)

class CartData(CartSchema):
    carts_id: int
    carts_note: Optional[str]
    carts_qty: int
    variants_id: int
    variants_option: Optional[str]
    variants_price: int
    variants_stock: int
    variants_image: Optional[str]
    variants_discount: int
    variants_discount_active: bool
    products_id: int
    products_name: str
    products_slug: str
    products_image_product: str
    products_preorder: Optional[int]
    products_discount_status: Literal['ongoing','will_come','not_active','have_ended']
    products_wholesale: Optional[dict]

    @validator('products_image_product',pre=True)
    def convert_image_product(cls, v):
        return json.loads(v)['0']

class CartDataNav(CartSchema):
    carts_id: int
    carts_qty: int
    variants_option: Optional[str]
    variants_price: int
    variants_image: Optional[str]
    products_name: str
    products_image_product: str
    products_weight: int

    @validator('products_image_product',pre=True)
    def convert_image_product(cls, v):
        return json.loads(v)['0']

class CartQtyItem(CartSchema):
    total_item: int
    total_qty: int

class CartQtyItemData(CartSchema):
    user_id: int
    total_item: int
    total_qty: int
    ready_stock: CartQtyItem
    empty_stock: CartQtyItem
