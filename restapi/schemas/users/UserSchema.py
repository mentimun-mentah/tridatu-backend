from pydantic import BaseModel, EmailStr, constr, validator
from typing import Literal, Optional
from schemas import errors

class UserSchema(BaseModel):
    email: EmailStr

    class Config:
        min_anystr_length = 1
        anystr_strip_whitespace = True

class UserRegister(UserSchema):
    username: constr(strict=True, min_length=3, max_length=100)
    confirm_password: constr(strict=True, min_length=6, max_length=100)
    password: constr(strict=True, min_length=6, max_length=100)

    @validator('password')
    def validate_password(cls, v, values, **kwargs):
        if 'confirm_password' in values and values['confirm_password'] != v:
            raise errors.PasswordConfirmError()
        return v

class UserEmail(UserSchema):
    pass

class UserLogin(UserSchema):
    password: constr(strict=True, min_length=6, max_length=100)

class UserResetPassword(UserSchema):
    confirm_password: constr(strict=True, min_length=6, max_length=100)
    password: constr(strict=True, min_length=6, max_length=100)

    @validator('password')
    def validate_password(cls, v, values, **kwargs):
        if 'confirm_password' in values and values['confirm_password'] != v:
            raise errors.PasswordConfirmError()
        return v

class UserData(UserSchema):
    username: str
    password: Optional[bool]
    phone: Optional[str]
    gender: Optional[Literal['Laki-laki','Perempuan','Lainnya']]
    role: str
    avatar: str
