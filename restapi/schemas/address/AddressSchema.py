from phonenumbers import (
    NumberParseException,
    PhoneNumberType,
    PhoneNumberFormat,
    format_number,
    number_type,
    is_valid_number,
    parse as parse_phone_number
)
from pydantic import BaseModel, validator, constr, conint
from typing import List, Optional
from schemas import errors

class AddressSchema(BaseModel):
    label: constr(strict=True, max_length=100)
    receiver: constr(strict=True, max_length=100)
    phone: constr(strict=True, max_length=20)
    region: constr(strict=True)
    postal_code: conint(strict=True, gt=0, lt=999999)
    recipient_address: constr(strict=True)

    @validator('phone')
    def validate_phone(cls, v):
        try:
            n = parse_phone_number(v, "ID")
        except NumberParseException:
            raise errors.PhoneNumberError()

        MOBILE_NUMBER_TYPES = PhoneNumberType.MOBILE, PhoneNumberType.FIXED_LINE_OR_MOBILE

        if not is_valid_number(n) or number_type(n) not in MOBILE_NUMBER_TYPES:
            raise errors.PhoneNumberError()

        return format_number(n, PhoneNumberFormat.INTERNATIONAL)

    class Config:
        min_anystr_length = 1
        anystr_strip_whitespace = True

class AddressCreateUpdate(AddressSchema):
    pass

class AddressData(AddressSchema):
    main_address: bool
    id: str

class AddressPaginate(BaseModel):
    data: List[AddressData]
    total: int
    next_num: Optional[int]
    prev_num: Optional[int]
    page: int
    iter_pages: list

class AddressSearchData(BaseModel):
    value: str
    postal_code: List[int]
