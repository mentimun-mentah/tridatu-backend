from pydantic import BaseModel, constr, conint

class ReplySchema(BaseModel):
    class Config:
        min_anystr_length = 5
        anystr_strip_whitespace = True

class ReplyCreate(ReplySchema):
    message: constr(strict=True)
    comment_id: conint(strict=True, gt=0)
