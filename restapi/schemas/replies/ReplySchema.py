from pydantic import BaseModel, constr, validator
from typing import List
from datetime import datetime

class ReplySchema(BaseModel):
    class Config:
        min_anystr_length = 1
        anystr_strip_whitespace = True

class ReplyCreate(ReplySchema):
    message: constr(strict=True, min_length=5)
    comment_id: constr(strict=True, regex=r'^[0-9]*$')

    @validator('comment_id')
    def parse_str_to_int(cls, v):
        return int(v) if v else None

class ReplyData(ReplySchema):
    replies_id: str
    replies_message: str
    replies_user_id: str
    replies_created_at: datetime
    users_username: str
    users_avatar: str
    users_role: str

class ReplyCommentData(ReplySchema):
    comments_id: str
    comments_replies: List[ReplyData]
