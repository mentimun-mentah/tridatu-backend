from fastapi import Query
from typing import Literal

def get_all_query_cart(stock: Literal['empty','ready'] = Query(None,description="Example 'empty', 'ready'")):
    return {"stock": stock}
