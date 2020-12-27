from pydantic import BaseModel

class ShippingSchema(BaseModel):
    value: str
    shipping_cities_id: int
    shipping_subdistricts_id: int

    class Config:
        anystr_strip_whitespace = True

class ShippingSearchData(ShippingSchema):
    pass
