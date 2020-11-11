from pydantic import BaseModel, constr, EmailStr

class UserSchema(BaseModel):
    # id: StrictInt
    # username: constr(strict=True, min_length=3)
    # email: EmailStr
    # password: constr(strict=True, min_length=6)
    # role: constr(strict=True, max_length=10)
    # avatar: constr(strict=True)

    # created_at: datetime
    # updated_at: datetime

    class Config:
        min_anystr_length = 1
        max_anystr_length = 100
        anystr_strip_whitespace = True

class UserEmail(UserSchema):
    email: EmailStr

class UserLogin(UserSchema):
    email: EmailStr
    password: constr(strict=True, min_length=6)
