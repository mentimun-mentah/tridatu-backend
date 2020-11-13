from pydantic import BaseModel, constr, validator

class UserPasswordSchema(BaseModel):
    confirm_password: constr(strict=True, min_length=6)
    password: constr(strict=True, min_length=6)

    @validator('password')
    def validate_password(cls, v, values, **kwargs):
        if 'confirm_password' in values and values['confirm_password'] != v:
            raise ValueError("Password must match with confirmation.")
        return v

    class Config:
        min_anystr_length = 1
        max_anystr_length = 100
        anystr_strip_whitespace = True

class UserAddPassword(UserPasswordSchema):
    pass

class UserUpdatePassword(UserPasswordSchema):
    old_password: constr(strict=True, min_length=6)
