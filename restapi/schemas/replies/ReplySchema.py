from pydantic import BaseModel, constr, conint, validator
from typing import List

class ReplySchema(BaseModel):
    class Config:
        min_anystr_length = 5
        anystr_strip_whitespace = True

class ReplyCreate(ReplySchema):
    message: constr(strict=True)
    comment_id: conint(strict=True, gt=0)

class ReplyData(ReplySchema):
    replies_id: int
    replies_message: str
    replies_created_at: str
    users_username: str
    users_avatar: str
    users_role: str

    @validator('replies_created_at',pre=True)
    def convert_datetime_to_str(cls, v):
        return v.isoformat()

class ReplyCommentData(ReplySchema):
    comments_id: int
    comments_replies: List[ReplyData]
