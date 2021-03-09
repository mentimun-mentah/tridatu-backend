from pydantic import BaseModel, StrictBool, constr, conint, conlist, validator
from typing import Optional
from schemas import errors

class VariantSchema(BaseModel):
    class Config:
        min_anystr_length = 1
        anystr_strip_whitespace = True

class VariantTwoData(VariantSchema):
    va2_id: Optional[constr(strict=True, regex=r'^[0-9]*$')]
    va2_option: constr(strict=True, max_length=20)
    va2_price: constr(strict=True, regex=r'^[0-9]*$')
    va2_stock: constr(strict=True, regex=r'^[0-9]*$')
    va2_code: Optional[constr(strict=True, max_length=50)]
    va2_barcode: Optional[constr(strict=True, max_length=50)]
    # for discount product
    va2_discount: Optional[conint(strict=True, ge=0, le=95)]
    va2_discount_active: Optional[StrictBool]

    @validator('va2_id','va2_price','va2_stock')
    def parse_str_to_int(cls, v):
        return int(v) if v else None

class VariantOneData(VariantSchema):
    va1_id: Optional[constr(strict=True, regex=r'^[0-9]*$')]
    va1_option: Optional[constr(strict=True, max_length=20)]
    va1_price: Optional[constr(strict=True, regex=r'^[0-9]*$')]
    va1_stock: Optional[constr(strict=True, regex=r'^[0-9]*$')]
    va1_code: Optional[constr(strict=True, max_length=50)]
    va1_barcode: Optional[constr(strict=True, max_length=50)]
    # for discount product
    va1_discount: Optional[conint(strict=True, ge=0, le=95)]
    va1_discount_active: Optional[StrictBool]
    # for update product
    va1_image: Optional[constr(strict=True, max_length=100)]

    va2_items: Optional[conlist(VariantTwoData, min_items=1, max_items=20)]

    @validator('va1_id','va1_price','va1_stock')
    def parse_str_to_int(cls, v):
        return int(v) if v else None

    @validator('va2_items')
    def validate_duplicate_items(cls, v):
        duplicate_items = [x.va2_option for x in v]
        if len(set(duplicate_items)) != len(duplicate_items):
            raise errors.VariantDuplicateOptionError()
        return v

class VariantCreateUpdate(VariantSchema):
    va1_name: Optional[constr(strict=True, max_length=15)]
    va2_name: Optional[constr(strict=True, max_length=15)]
    va1_product_id: Optional[constr(strict=True, regex=r'^[0-9]*$')]
    va1_items: conlist(VariantOneData, min_items=1, max_items=20)

    @validator('va1_product_id')
    def parse_va1_product_id(cls, v):
        return int(v) if v else None

    @validator('va1_items')
    def validate_va1_items(cls, v, values, **kwargs):
        # validate duplicate in items
        duplicate_items = [x.va1_option for x in v]
        if len(set(duplicate_items)) != len(duplicate_items):
            raise errors.VariantDuplicateOptionError()

        if [x for x in v if x.va2_items is not None] != []:
            # data is double variant
            if 'va1_name' in values and values['va1_name'] is None:
                raise errors.VariantOneNameMissingError()
            if 'va2_name' in values and values['va2_name'] is None:
                raise errors.VariantTwoNameMissingError()

            for index, value in enumerate(v):
                if value.va1_option is None:
                    raise errors.VariantOneOptionMissingError(index=index)

                for index_v2, value_v2 in enumerate(value.va2_items):
                    # validation for data from db
                    if value_v2.va2_id is not None and ('va1_product_id' in values and values['va1_product_id'] is None):
                        raise errors.VariantProductIdMissingError()
                    if value_v2.va2_id is None and ('va1_product_id' in values and values['va1_product_id'] is not None):
                        raise errors.VariantTwoIdMissingError(option=value.va1_option,index=index_v2)

                    # validation for discount
                    if value_v2.va2_discount is not None and value_v2.va2_discount_active is None:
                        raise errors.VariantTwoDiscountActiveMissingError(option=value.va1_option,index=index_v2)
                    if value_v2.va2_discount is None and value_v2.va2_discount_active is not None:
                        raise errors.VariantTwoDiscountMissingError(option=value.va1_option,index=index_v2)
                    if value_v2.va2_discount_active is True and value_v2.va2_discount < 1:
                        raise errors.VariantTwoDiscountNotGtError(option=value.va1_option,index=index_v2,limit_value=0)
                    # set discount null if discount_active is false
                    if value_v2.va2_discount_active is False:
                        value_v2.va2_discount, value_v2.va2_discount_active = 0, False

                # item below must doesn't exists
                value.va1_price, value.va1_stock, value.va1_code, value.va1_barcode = None, None, None, None
                value.va1_id, value.va1_discount, value.va1_discount_active = None, None, None

        elif (
            ('va1_name' in values and values['va1_name'] is None) and
            ('va2_name' in values and values['va2_name'] is None) and
            (len(v) == 1 and len([x for x in v if x.va1_option is None]) == 1)
        ):
            # data is without variant
            if v[0].va1_price is None:
                raise errors.VariantOnePriceWithoutIndexMissingError()
            if v[0].va1_stock is None:
                raise errors.VariantOneStockWithoutIndexMissingError()
            # validation for data from db
            if v[0].va1_id is not None and ('va1_product_id' in values and values['va1_product_id'] is None):
                raise errors.VariantProductIdMissingError()
            if v[0].va1_id is None and ('va1_product_id' in values and values['va1_product_id'] is not None):
                raise errors.VariantOneIdWithoutIndexMissingError()

            # validation for discount
            if v[0].va1_discount is not None and v[0].va1_discount_active is None:
                raise errors.VariantOneDiscountActiveWithoutIndexMissingError()
            if v[0].va1_discount is None and v[0].va1_discount_active is not None:
                raise errors.VariantOneDiscountWithoutIndexMissingError()
            if v[0].va1_discount_active is True and v[0].va1_discount < 1:
                raise errors.VariantOneDiscountWithoutIndexNotGtError(limit_value=0)
            # set discount null if discount_active is false
            if v[0].va1_discount_active is False:
                v[0].va1_discount, v[0].va1_discount_active = 0, False

            # va1_image must doesn't exists
            v[0].va1_image = None

        else:
            # data is single variant
            if 'va1_name' in values and values['va1_name'] is None:
                raise errors.VariantOneNameMissingError()

            for index, value in enumerate(v):
                if value.va1_option is None:
                    raise errors.VariantOneOptionMissingError(index=index)
                if value.va1_price is None:
                    raise errors.VariantOnePriceMissingError(index=index)
                if value.va1_stock is None:
                    raise errors.VariantOneStockMissingError(index=index)

                # validation for data from db
                if value.va1_id is not None and ('va1_product_id' in values and values['va1_product_id'] is None):
                    raise errors.VariantProductIdMissingError()
                if value.va1_id is None and ('va1_product_id' in values and values['va1_product_id'] is not None):
                    raise errors.VariantOneIdMissingError(index=index)

                # validation for discount
                if value.va1_discount is not None and value.va1_discount_active is None:
                    raise errors.VariantOneDiscountActiveMissingError(index=index)
                if value.va1_discount is None and value.va1_discount_active is not None:
                    raise errors.VariantOneDiscountMissingError(index=index)
                if value.va1_discount_active is True and value.va1_discount < 1:
                    raise errors.VariantOneDiscountNotGtError(index=index,limit_value=0)
                # set discount null if discount_active is false
                if value.va1_discount_active is False:
                    value.va1_discount, value.va1_discount_active = 0, False

            # va2_name must doesn't exists
            values['va2_name'] = None

        return v

    @validator('va2_name')
    def validate_same_name(cls, v, values, **kwargs):
        if 'va1_name' in values and values['va1_name'] == v:
            raise errors.VariantDuplicateNameError()
        return v
