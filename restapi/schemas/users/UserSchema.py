from pydantic import BaseModel
# from typing import Optional

class UserSchema(BaseModel):
    class Config:
        min_anystr_length = 1
        max_anystr_length = 100
        anystr_strip_whitespace = True
