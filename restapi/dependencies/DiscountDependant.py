from fastapi import Query
from typing import Literal

def get_all_query_discount(
    page: int = Query(...,gt=0),
    per_page: int = Query(...,gt=0),
    q: str = Query(None,min_length=1),
    status: Literal['ongoing','will_come','not_active','have_ended'] = Query(
        None, description="Example 'ongoing', 'will_come', 'not_active', 'have_ended'"
    ),
):
    return {
        "page": page,
        "per_page": per_page,
        "q": q,
        "status": status,
    }
