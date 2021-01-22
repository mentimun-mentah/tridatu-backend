import json
from pydantic import BaseModel, conlist, conint, constr, validator
from controllers.VariantController import VariantLogic
from config import redis_conn

class WholeSaleSchema(BaseModel):
    class Config:
        min_anystr_length = 1
        max_anystr_length = 100
        anystr_strip_whitespace = True
        schema_extra = {"example": {"variant": "ticket variant", "items": [{"min_qty": 0,"price": 0}]}}

class WholeSaleData(WholeSaleSchema):
    min_qty: conint(strict=True, gt=1)
    price: conint(strict=True, gt=0)

class WholeSaleCreateUpdate(WholeSaleSchema):
    variant: constr(strict=True)
    items: conlist(WholeSaleData, min_items=1, max_items=5)

    @validator('variant')
    def validate_variant(cls, v):
        # check if variant exists on redis
        if redis_conn.get(v) is None:
            raise ValueError("variant not found!")

        # all price in variant must be same
        variant_data = VariantLogic.convert_data_to_db(json.loads(redis_conn.get(v)),0)
        variant_price_unique = list(set([item['price'] for item in variant_data]))
        if len(variant_price_unique) > 1:
            raise ValueError("wholesale prices are only available for all variant that are priced the same")

        return variant_price_unique[0]

    @validator('items')
    def validate_items(cls, v, values, **kwargs):
        if 'variant' not in values:
            raise ValueError("variant not found!")

        initial_price = round(values['variant'] / 2)
        for idx in range(len(v)):
            if v[idx].price < initial_price:
                raise ValueError(f"price {idx}: The price shall not be 50% lower than the initial price")
            if idx > 0:
                if v[idx].min_qty <= v[idx - 1].min_qty:
                    raise ValueError(f"min_qty {idx}: must be more > than before")
                if v[idx].price >= v[idx - 1].price:
                    raise ValueError(f"price {idx}: The price must be less than the previous price")
        return v
