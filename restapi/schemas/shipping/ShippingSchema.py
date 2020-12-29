from pydantic import BaseModel, constr, conint

class ShippingSchema(BaseModel):
    class Config:
        min_anystr_length = 3
        max_anystr_length = 100
        anystr_strip_whitespace = True

class ShippingGetCost(ShippingSchema):
    origin: conint(strict=True, gt=0)
    originType: constr(strict=True)
    destination: conint(strict=True, gt=0)
    destinationType: constr(strict=True)
    weight: conint(strict=True, gt=0)
    courier: constr(strict=True)

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
