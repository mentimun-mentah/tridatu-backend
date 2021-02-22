from pydantic import BaseModel, constr, validator
from schemas import errors

class UserPasswordSchema(BaseModel):
    confirm_password: constr(strict=True, min_length=6, max_length=100)
    password: constr(strict=True, min_length=6, max_length=100)

    @validator('password')
    def validate_password(cls, v, values, **kwargs):
        if 'confirm_password' in values and values['confirm_password'] != v:
            raise errors.PasswordConfirmError()
        return v

    class Config:
        min_anystr_length = 1
        anystr_strip_whitespace = True

class UserAddPassword(UserPasswordSchema):
    pass

class UserUpdatePassword(UserPasswordSchema):
    old_password: constr(strict=True, min_length=6, max_length=100)

class UserConfirmPassword(BaseModel):
    password: constr(strict=True, min_length=6, max_length=100, strip_whitespace=True)
