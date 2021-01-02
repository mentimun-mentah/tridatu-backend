from fastapi import Query
from typing import Literal

def get_all_query_comment(
    page: int = Query(...,gt=0),
    per_page: int = Query(...,gt=0),
    comment_id: int = Query(...,gt=0),
    comment_type: Literal['product'] = Query(...,description="Example 'product'")
):
    return {
        "page": page,
        "per_page": per_page,
        "comment_id": comment_id,
        "comment_type": comment_type
    }
