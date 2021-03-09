from pydantic import BaseModel, constr, conint

class ShippingSchema(BaseModel):
    class Config:
        min_anystr_length = 1
        anystr_strip_whitespace = True

class ShippingGetCost(ShippingSchema):
    origin: conint(strict=True, gt=0)
    originType: constr(strict=True, min_length=3, max_length=100)
    destination: conint(strict=True, gt=0)
    destinationType: constr(strict=True, min_length=3, max_length=100)
    weight: conint(strict=True, gt=0)
    courier: constr(strict=True, min_length=3, max_length=100)

class ShippingDataCost(ShippingSchema):
    origin_detail: str
    destination_detail: str
    min_cost: int
    max_cost: int
    costs_shipping: list

class ShippingSearchData(ShippingSchema):
    value: str
    shipping_cities_id: int
    shipping_subdistricts_id: int
