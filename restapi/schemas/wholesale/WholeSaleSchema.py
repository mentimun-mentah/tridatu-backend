import json
from pydantic import BaseModel, conlist, conint, constr, validator
from controllers.VariantController import VariantLogic
from config import redis_conn
from schemas import errors

class WholeSaleSchema(BaseModel):
    class Config:
        min_anystr_length = 1
        anystr_strip_whitespace = True
        schema_extra = {"example": {"variant": "ticket variant", "items": [{"min_qty": 0,"price": "0"}]}}

class WholeSaleData(WholeSaleSchema):
    min_qty: conint(strict=True, gt=1)
    price: constr(strict=True, regex=r'^[0-9]*$')

    @validator('price')
    def parse_str_to_int(cls, v):
        return int(v) if v else None

class WholeSaleCreateUpdate(WholeSaleSchema):
    variant: constr(strict=True, max_length=100)
    items: conlist(WholeSaleData, min_items=1, max_items=5)

    @validator('variant')
    def validate_variant(cls, v):
        # check if variant exists on redis
        if redis_conn.get(v) is None:
            raise errors.WholeSaleVariantMissingError()

        # all price in variant must be same
        variant_data = VariantLogic.convert_data_to_db(json.loads(redis_conn.get(v)),0)
        variant_price_unique = list(set([item['price'] for item in variant_data]))
        if len(variant_price_unique) > 1:
            raise errors.WholeSaleVariantNotSameError()

        return variant_price_unique[0]

    @validator('items')
    def validate_items(cls, v, values, **kwargs):
        if 'variant' not in values:
            raise errors.WholeSaleVariantMissingError()

        initial_price = round(values['variant'] / 2)
        for idx in range(len(v)):
            if v[idx].price < initial_price:
                raise errors.WholeSalePriceNotGeHalfInitialPriceError(idx=idx)
            if idx > 0:
                if v[idx].min_qty <= v[idx - 1].min_qty:
                    raise errors.WholeSaleMinQtyNotGtBeforeError(idx=idx)
                if v[idx].price >= v[idx - 1].price:
                    raise errors.WholeSalePriceNotLtBeforeError(idx=idx)
        return v
