from phonenumbers import (
    NumberParseException,
    PhoneNumberType,
    PhoneNumberFormat,
    format_number,
    number_type,
    is_valid_number,
    parse as parse_phone_number
)
from pydantic import BaseModel, validator, StrictBool, constr, conint
from typing import List

class AddressSchema(BaseModel):
    class Config:
        min_anystr_length = 1
        anystr_strip_whitespace = True

class AddressCreate(AddressSchema):
    label: constr(strict=True, max_length=100)
    receiver: constr(strict=True, max_length=100)
    phone: constr(strict=True, max_length=20)
    region: constr(strict=True)
    postal_code: conint(strict=True, gt=0)
    recipient_address: constr(strict=True)
    main_address: StrictBool

    @validator('phone')
    def validate_phone(cls, v):
        try:
            n = parse_phone_number(v, "ID")
        except NumberParseException as e:
            raise ValueError('Please provide a valid mobile phone number') from e

        MOBILE_NUMBER_TYPES = PhoneNumberType.MOBILE, PhoneNumberType.FIXED_LINE_OR_MOBILE

        if not is_valid_number(n) or number_type(n) not in MOBILE_NUMBER_TYPES:
            raise ValueError('Please provide a valid mobile phone number')

        return format_number(n, PhoneNumberFormat.INTERNATIONAL)

class AddressSearchData(BaseModel):
    value: str
    postal_code: List[int]
