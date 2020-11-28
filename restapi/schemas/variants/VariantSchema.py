from pydantic import BaseModel, constr, conint, conlist, validator
from typing import Optional

class VariantSchema(BaseModel):
    class Config:
        min_anystr_length = 1
        max_anystr_length = 100
        anystr_strip_whitespace = True

class VariantTwoData(VariantSchema):
    va2_option: constr(strict=True, max_length=20)
    va2_price: conint(strict=True, gt=0)
    va2_stock: conint(strict=True, ge=0)
    va2_code: Optional[constr(strict=True, max_length=50)]
    va2_barcode: Optional[constr(strict=True, max_length=50)]

class VariantOneData(VariantSchema):
    va1_option: Optional[constr(strict=True, max_length=20)]
    va1_price: Optional[conint(strict=True, gt=0)]
    va1_stock: Optional[conint(strict=True, ge=0)]
    va1_code: Optional[constr(strict=True, max_length=50)]
    va1_barcode: Optional[constr(strict=True, max_length=50)]

    va2_items: Optional[conlist(VariantTwoData, min_items=1, max_items=20)]

    @validator('va2_items')
    def validate_duplicate_items(cls, v):
        duplicate_items = [x.va2_option for x in v]
        if len(set(duplicate_items)) != len(duplicate_items):
            raise ValueError("the option must be different with each other")
        return v

class VariantCreateUpdate(VariantSchema):
    va1_name: Optional[constr(strict=True, max_length=15)]
    va2_name: Optional[constr(strict=True, max_length=15)]
    va1_items: conlist(VariantOneData, min_items=1, max_items=20)

    @validator('va1_items')
    def validate_va1_items(cls, v, values, **kwargs):
        # validate duplicate in items
        duplicate_items = [x.va1_option for x in v]
        if len(set(duplicate_items)) != len(duplicate_items):
            raise ValueError("the option must be different with each other")

        if [x for x in v if x.va2_items is not None] != []:
            # data is double variant
            if 'va1_name' in values and values['va1_name'] is None:
                raise ValueError("ensure va1_name value is not null")
            if 'va2_name' in values and values['va2_name'] is None:
                raise ValueError("ensure va2_name value is not null")

            for index, value in enumerate(v):
                assert value.va1_option is not None, f"ensure va1_option at index {index} value is not null"
                # item below must doesn't exists
                # va1_items.va1_price, va1_items.va1_stock, va1_items.va1_code, va1_items.va1_barcode
                value.va1_price, value.va1_stock, value.va1_code, value.va1_barcode = None, None, None, None

        elif (
            ('va1_name' in values and values['va1_name'] is None) and
            ('va2_name' in values and values['va2_name'] is None) and
            (len(v) == 1 and len([x for x in v if x.va1_option is None]) == 1)
        ):
            # data is without variant
            assert v[0].va1_price is not None, "ensure va1_price value is not null"
            assert v[0].va1_stock is not None, "ensure va1_stock value is not null"

        else:
            # data is single variant
            if 'va1_name' in values and values['va1_name'] is None:
                raise ValueError("ensure va1_name value is not null")

            for index, value in enumerate(v):
                assert value.va1_option is not None, f"ensure va1_option at index {index} value is not null"
                assert value.va1_price is not None, f"ensure va1_price at index {index} value is not null"
                assert value.va1_stock is not None, f"ensure va1_stock at index {index} value is not null"

            # item below must doesn't exists
            # va2_name
            values['va2_name'] = None

        return v

    @validator('va2_name')
    def validate_same_name(cls, v, values, **kwargs):
        if 'va1_name' in values and values['va1_name'] == v:
            raise ValueError("Names cannot be the same.")
        return v
