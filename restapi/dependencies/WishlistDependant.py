from fastapi import Query
from typing import Literal

def get_user_query_wishlist(
    page: int = Query(...,gt=0),
    per_page: int = Query(...,gt=0),
    q: str = Query(None,min_length=1),
    order_by: Literal['high_price','low_price','longest'] = Query(
        None, description="Example 'high_price', 'low_price', 'longest'"
    )
):
    return {
        "page": page,
        "per_page": per_page,
        "q": q,
        "order_by": order_by
    }
