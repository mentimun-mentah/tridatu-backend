from pydantic import BaseModel, StrictBool, constr, conint, conlist, validator
from typing import Optional

class VariantSchema(BaseModel):
    class Config:
        min_anystr_length = 1
        max_anystr_length = 100
        anystr_strip_whitespace = True

class VariantTwoData(VariantSchema):
    va2_id: Optional[conint(strict=True, gt=0)]
    va2_option: constr(strict=True, max_length=20)
    va2_price: conint(strict=True, gt=0)
    va2_stock: conint(strict=True, ge=0)
    va2_code: Optional[constr(strict=True, max_length=50)]
    va2_barcode: Optional[constr(strict=True, max_length=50)]
    # for discount product
    va2_discount: Optional[conint(strict=True, ge=0, le=95)]
    va2_discount_active: Optional[StrictBool]

class VariantOneData(VariantSchema):
    va1_id: Optional[conint(strict=True, gt=0)]
    va1_option: Optional[constr(strict=True, max_length=20)]
    va1_price: Optional[conint(strict=True, gt=0)]
    va1_stock: Optional[conint(strict=True, ge=0)]
    va1_code: Optional[constr(strict=True, max_length=50)]
    va1_barcode: Optional[constr(strict=True, max_length=50)]
    # for discount product
    va1_discount: Optional[conint(strict=True, ge=0, le=95)]
    va1_discount_active: Optional[StrictBool]
    # for update product
    va1_image: Optional[constr(strict=True, max_length=100)]

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
    va1_product_id: Optional[conint(strict=True, gt=0)]
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

                for index_v2, value_v2 in enumerate(value.va2_items):
                    # validation for data from db
                    if value_v2.va2_id is not None and ('va1_product_id' in values and values['va1_product_id'] is None):
                        raise ValueError("ensure va1_product_id value is not null")
                    if value_v2.va2_id is None and ('va1_product_id' in values and values['va1_product_id'] is not None):
                        raise ValueError(f"ensure va2_id at option {value.va1_option} and index {index_v2} value is not null")

                    # validation for discount
                    if value_v2.va2_discount is not None and value_v2.va2_discount_active is None:
                        raise ValueError(f"ensure va2_discount_active at option {value.va1_option} and index {index_v2} value is not null")
                    if value_v2.va2_discount is None and value_v2.va2_discount_active is not None:
                        raise ValueError(f"ensure va2_discount at option {value.va1_option} and index {index_v2} value is not null")
                    if value_v2.va2_discount_active is True and value_v2.va2_discount < 1:
                        raise ValueError(f"ensure va2_discount at option {value.va1_option} and index {index_v2} value is greater than 0")
                    # set discount null if discount_active is false
                    if value_v2.va2_discount_active is False:
                        value_v2.va2_discount, value_v2.va2_discount_active = 0, False

                # item below must doesn't exists
                value.va1_price, value.va1_stock, value.va1_code, value.va1_barcode = None, None, None, None
                value.va1_discount, value.va1_discount_active = None, None

        elif (
            ('va1_name' in values and values['va1_name'] is None) and
            ('va2_name' in values and values['va2_name'] is None) and
            (len(v) == 1 and len([x for x in v if x.va1_option is None]) == 1)
        ):
            # data is without variant
            assert v[0].va1_price is not None, "ensure va1_price value is not null"
            assert v[0].va1_stock is not None, "ensure va1_stock value is not null"
            # validation for data from db
            if v[0].va1_id is not None and ('va1_product_id' in values and values['va1_product_id'] is None):
                raise ValueError("ensure va1_product_id value is not null")
            if v[0].va1_id is None and ('va1_product_id' in values and values['va1_product_id'] is not None):
                raise ValueError("ensure va1_id value is not null")

            # validation for discount
            if v[0].va1_discount is not None and v[0].va1_discount_active is None:
                raise ValueError("ensure va1_discount_active value is not null")
            if v[0].va1_discount is None and v[0].va1_discount_active is not None:
                raise ValueError("ensure va1_discount value is not null")
            if v[0].va1_discount_active is True and v[0].va1_discount < 1:
                raise ValueError("ensure va1_discount value is greater than 0")
            # set discount null if discount_active is false
            if v[0].va1_discount_active is False:
                v[0].va1_discount, v[0].va1_discount_active = 0, False

            # va1_image must doesn't exists
            v[0].va1_image = None

        else:
            # data is single variant
            if 'va1_name' in values and values['va1_name'] is None:
                raise ValueError("ensure va1_name value is not null")

            for index, value in enumerate(v):
                assert value.va1_option is not None, f"ensure va1_option at index {index} value is not null"
                assert value.va1_price is not None, f"ensure va1_price at index {index} value is not null"
                assert value.va1_stock is not None, f"ensure va1_stock at index {index} value is not null"
                # validation for data from db
                if value.va1_id is not None and ('va1_product_id' in values and values['va1_product_id'] is None):
                    raise ValueError("ensure va1_product_id value is not null")
                if value.va1_id is None and ('va1_product_id' in values and values['va1_product_id'] is not None):
                    raise ValueError(f"ensure va1_id at index {index} value is not null")

                # validation for discount
                if value.va1_discount is not None and value.va1_discount_active is None:
                    raise ValueError(f"ensure va1_discount_active at index {index} value is not null")
                if value.va1_discount is None and value.va1_discount_active is not None:
                    raise ValueError(f"ensure va1_discount at index {index} value is not null")
                if value.va1_discount_active is True and value.va1_discount < 1:
                    raise ValueError(f"ensure va1_discount at index {index} value is greater than 0")
                # set discount null if discount_active is false
                if value.va1_discount_active is False:
                    value.va1_discount, value.va1_discount_active = 0, False

            # va2_name must doesn't exists
            values['va2_name'] = None

        return v

    @validator('va2_name')
    def validate_same_name(cls, v, values, **kwargs):
        if 'va1_name' in values and values['va1_name'] == v:
            raise ValueError("Names cannot be the same.")
        return v
