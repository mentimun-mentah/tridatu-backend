import json
from pydantic import BaseModel, constr, conlist, validator
from typing import Optional, Literal

class CartSchema(BaseModel):
    class Config:
        min_anystr_length = 1
        anystr_strip_whitespace = True

class CartCreateUpdate(CartSchema):
    variant_id: constr(strict=True, regex=r'^[0-9]*$')
    qty: constr(strict=True, regex=r'^[0-9]*$')
    operation: Literal['update','create']
    note: Optional[constr(strict=True, max_length=100)]

    @validator('variant_id','qty')
    def parse_str_to_int(cls, v):
        return int(v) if v else None

class CartDelete(CartSchema):
    cartIds: conlist(constr(strict=True, regex=r'^[0-9]*$'), min_items=1, max_items=20)

    @validator('cartIds', each_item=True)
    def parse_str_to_int(cls, v):
        return int(v) if v else None

# ============ CARTS ============

class CartWholeSale(CartSchema):
    min_qty: int
    price: str

class CartData(CartSchema):
    carts_id: str
    carts_note: Optional[str]
    carts_qty: str
    variants_id: str
    variants_option: Optional[str]
    variants_price: str
    variants_stock: str
    variants_image: Optional[str]
    variants_discount: int
    variants_discount_active: bool
    products_id: str
    products_name: str
    products_slug: str
    products_image_product: str
    products_preorder: Optional[int]
    products_discount_status: Literal['ongoing','will_come','not_active','have_ended']
    products_wholesale: Optional[CartWholeSale]

    @validator('products_image_product',pre=True)
    def convert_image_product(cls, v):
        return json.loads(v)['0']

# ============ CARTS FROM NAVBAR ============

class CartDataNav(CartSchema):
    carts_id: str
    carts_qty: str
    variants_option: Optional[str]
    variants_price: str
    variants_image: Optional[str]
    products_name: str
    products_image_product: str
    products_weight: str

    @validator('products_image_product',pre=True)
    def convert_image_product(cls, v):
        return json.loads(v)['0']

# ============ CARTS NOTIF ============

class CartQtyItem(CartSchema):
    total_item: int
    total_qty: str

class CartQtyItemData(CartSchema):
    user_id: str
    total_item: int
    total_qty: str
    ready_stock: CartQtyItem
    empty_stock: CartQtyItem
