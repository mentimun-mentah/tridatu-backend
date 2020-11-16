from fastapi import APIRouter, Query
from controllers.AddressController import AddressFetch
from schemas.address.AddressSchema import AddressSearchData
from typing import List

router = APIRouter()

@router.get('/search/city-or-district',response_model=List[AddressSearchData])
async def search_city_or_district(q: str = Query(...,min_length=3,max_length=100)):
    return await AddressFetch.search_city_or_district(q)
