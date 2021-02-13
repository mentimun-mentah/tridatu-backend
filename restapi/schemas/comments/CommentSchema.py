from pydantic import BaseModel, constr, validator
from typing import Literal, List, Optional
from datetime import datetime

class CommentSchema(BaseModel):
    class Config:
        min_anystr_length = 1
        anystr_strip_whitespace = True

class CommentCreate(CommentSchema):
    message: constr(strict=True, min_length=5)
    commentable_id: constr(strict=True, regex=r'^[0-9]*$')
    commentable_type: Literal['product']

    @validator('commentable_id')
    def parse_commentable_id(cls, v):
        return int(v) if v else None

class CommentData(CommentSchema):
    comments_id: str
    comments_message: str
    comments_created_at: datetime
    users_username: str
    users_avatar: str
    total_replies: int

class CommentPaginate(BaseModel):
    data: List[CommentData]
    total: int
    next_num: Optional[int]
    prev_num: Optional[int]
    page: int
    iter_pages: list
