from pydantic import BaseModel, constr, conint
from typing import Literal

class CommentSchema(BaseModel):
    class Config:
        min_anystr_length = 5
        anystr_strip_whitespace = True

class CommentCreate(CommentSchema):
    subject: constr(strict=True)
    comment_id: conint(strict=True, gt=0)
    comment_type: Literal['product']
