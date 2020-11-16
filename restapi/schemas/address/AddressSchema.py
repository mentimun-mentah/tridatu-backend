from pydantic import BaseModel
from typing import List

class AddressSearchData(BaseModel):
    value: str
    postal_code: List[int]
