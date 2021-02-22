from pydantic import PydanticValueError
from decimal import Decimal
from typing import Union

# ========= USER SECTION =========

class PhoneNumberError(PydanticValueError):
    code = 'phone_number'
    msg_template = 'value is not a valid mobile phone number'

class PasswordConfirmError(PydanticValueError):
    code = 'password_confirm'
    msg_template = 'password must match with password confirmation'

# ========= DISCOUNT SECTION =========

class DiscountStartTimeError(PydanticValueError):
    code = 'discount_start.time'
    msg_template = 'the start time must be after the current time'

class DiscountEndMinExpError(PydanticValueError):
    code = 'discount_end.min_exp'
    msg_template = 'the expiration time must be at least one hour longer than the start time'

class DiscountEndMaxExpError(PydanticValueError):
    code = 'discount_end.max_exp'
    msg_template = 'promo period must be less than 180 days'

# ========= VARIANT SECTION =========

class VariantDuplicateOptionError(PydanticValueError):
    code = 'variant.duplicate_option'
    msg_template = 'the option must be different with each other'

class VariantDuplicateNameError(PydanticValueError):
    code = 'variant.duplicate_name'
    msg_template = 'the name must be different with each other'

class VariantOneNameMissingError(PydanticValueError):
    code = 'variant.name_one.missing'
    msg_template = 'ensure va1_name value is not null'

class VariantTwoNameMissingError(PydanticValueError):
    code = 'variant.name_two.missing'
    msg_template = 'ensure va2_name value is not null'

class VariantProductIdMissingError(PydanticValueError):
    code = 'variant.product_id.missing'
    msg_template = 'ensure va1_product_id value is not null'

class _VariantTwoError(PydanticValueError):
    def __init__(self, *, option: str, index: int) -> None:
        super().__init__(option=option, index=index)

class VariantTwoIdMissingError(_VariantTwoError):
    code = 'variant.id_two.missing'
    msg_template = 'ensure va2_id at option {option} and index {index} value is not null'

class VariantTwoDiscountActiveMissingError(_VariantTwoError):
    code = 'variant.discount_active_two.missing'
    msg_template = 'ensure va2_discount_active at option {option} and index {index} value is not null'

class VariantTwoDiscountMissingError(_VariantTwoError):
    code = 'variant.discount_two.missing'
    msg_template = 'ensure va2_discount at option {option} and index {index} value is not null'

class VariantTwoDiscountNotGtError(PydanticValueError):
    code = 'variant.discount_two.not_gt'
    msg_template = 'ensure va2_discount at option {option} and index {index} value is greater than {limit_value}'

    def __init__(self, *, option: str, index: int, limit_value: Union[int, float, Decimal]) -> None:
        super().__init__(option=option, index=index, limit_value=limit_value)

class VariantOneIdWithoutIndexMissingError(PydanticValueError):
    code = 'variant.id_one.without_index.missing'
    msg_template = 'ensure va1_id value is not null'

class VariantOneDiscountActiveWithoutIndexMissingError(PydanticValueError):
    code = 'variant.discount_active_one.without_index.missing'
    msg_template = 'ensure va1_discount_active value is not null'

class VariantOneDiscountWithoutIndexMissingError(PydanticValueError):
    code = 'variant.discount_one.without_index.missing'
    msg_template = 'ensure va1_discount value is not null'

class VariantOneDiscountWithoutIndexNotGtError(PydanticValueError):
    code = 'variant.discount_one.without_index.not_gt'
    msg_template = 'ensure va1_discount value is greater than {limit_value}'

    def __init__(self, *, limit_value: Union[int, float, Decimal]) -> None:
        super().__init__(limit_value=limit_value)

class _VariantOneError(PydanticValueError):
    def __init__(self, *, index: int) -> None:
        super().__init__(index=index)

class VariantOneIdMissingError(_VariantOneError):
    code = 'variant.id_one.missing'
    msg_template = 'ensure va1_id at index {index} value is not null'

class VariantOneDiscountActiveMissingError(_VariantOneError):
    code = 'variant.discount_active_one.missing'
    msg_template = 'ensure va1_discount_active at index {index} value is not null'

class VariantOneDiscountMissingError(_VariantOneError):
    code = 'variant.discount_one.missing'
    msg_template = 'ensure va1_discount at index {index} value is not null'

class VariantOneDiscountNotGtError(PydanticValueError):
    code = 'variant.discount_one.not_gt'
    msg_template = 'ensure va1_discount at index {index} value is greater than {limit_value}'

    def __init__(self, *, index: int, limit_value: Union[int, float, Decimal]) -> None:
        super().__init__(index=index, limit_value=limit_value)

class VariantOneOptionMissingError(_VariantOneError):
    code = 'variant.option_one.missing'
    msg_template = 'ensure va1_option at index {index} value is not null'

class VariantOnePriceMissingError(_VariantOneError):
    code = 'variant.price_one.missing'
    msg_template = 'ensure va1_price at index {index} value is not null'

class VariantOneStockMissingError(_VariantOneError):
    code = 'variant.stock_one.missing'
    msg_template = 'ensure va1_stock at index {index} value is not null'

class VariantOnePriceWithoutIndexMissingError(PydanticValueError):
    code = 'variant.price_one.without_index.missing'
    msg_template = 'ensure va1_price value is not null'

class VariantOneStockWithoutIndexMissingError(PydanticValueError):
    code = 'variant.stock_one.without_index.missing'
    msg_template = 'ensure va1_stock value is not null'

# ========= WHOLESALE SECTION =========

class WholeSaleVariantMissingError(PydanticValueError):
    code = 'wholesale_variant.missing'
    msg_template = 'variant not found'

class WholeSaleVariantNotSameError(PydanticValueError):
    code = 'wholesale_variant.not_same'
    msg_template = 'wholesale prices are only available for all variant that are priced the same'

class _WholeSaleError(PydanticValueError):
    def __init__(self, *, idx: int) -> None:
        super().__init__(idx=idx)

class WholeSalePriceNotGeHalfInitialPriceError(_WholeSaleError):
    code = 'wholesale_price_initial.not_ge'
    msg_template = 'price {idx}: The price shall not be 50% lower than the initial price'

class WholeSaleMinQtyNotGtBeforeError(_WholeSaleError):
    code = 'wholesale_min_qty.not_gt'
    msg_template = 'min_qty {idx}: must be more > than before'

class WholeSalePriceNotLtBeforeError(_WholeSaleError):
    code = 'wholesale_price.not_lt'
    msg_template = 'price {idx}: The price must be less than the previous price'
