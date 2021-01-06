from pydantic import BaseModel, constr, conint, validator
from typing import Literal, List, Optional

class CommentSchema(BaseModel):
    class Config:
        min_anystr_length = 5
        anystr_strip_whitespace = True

class CommentCreate(CommentSchema):
    message: constr(strict=True)
    commentable_id: conint(strict=True, gt=0)
    commentable_type: Literal['product']

class CommentData(CommentSchema):
    comments_id: int
    comments_message: str
    comments_created_at: str
    users_username: str
    users_avatar: str
    total_replies: int

    @validator('comments_created_at',pre=True)
    def convert_datetime_to_str(cls, v):
        return v.isoformat()

class CommentPaginate(BaseModel):
    data: List[CommentData]
    total: int
    next_num: Optional[int]
    prev_num: Optional[int]
    page: int
    iter_pages: list
