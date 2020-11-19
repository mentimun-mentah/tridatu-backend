from pydantic import BaseModel, constr, validator

class UserPasswordSchema(BaseModel):
    confirm_password: constr(strict=True)
    password: constr(strict=True)

    @validator('password')
    def validate_password(cls, v, values, **kwargs):
        if 'confirm_password' in values and values['confirm_password'] != v:
            raise ValueError("Password must match with confirmation.")
        return v

    class Config:
        min_anystr_length = 6
        max_anystr_length = 100
        anystr_strip_whitespace = True

class UserAddPassword(UserPasswordSchema):
    pass

class UserUpdatePassword(UserPasswordSchema):
    old_password: constr(strict=True)

class UserConfirmPassword(BaseModel):
    password: constr(strict=True, min_length=6, max_length=100, strip_whitespace=True)
