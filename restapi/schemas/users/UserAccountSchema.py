from phonenumbers import (
    NumberParseException,
    PhoneNumberType,
    PhoneNumberFormat,
    format_number,
    number_type,
    is_valid_number,
    parse as parse_phone_number
)
from pydantic import BaseModel, constr, validator
from typing import Literal
from schemas import errors

class UserAccountSchema(BaseModel):
    username: constr(strict=True, min_length=3, max_length=100)
    phone: constr(strict=True, max_length=20)
    gender: Literal['Laki-laki','Perempuan','Lainnya']

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
