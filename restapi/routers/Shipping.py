from fastapi import APIRouter, Query
from controllers.ShippingController import ShippingFetch
from schemas.shipping.ShippingSchema import ShippingSearchData
from typing import List

router = APIRouter()

@router.get('/search/city-or-district',response_model=List[ShippingSearchData])
async def search_shipping_city_or_district(
    q: str = Query(...,min_length=1,max_length=100),
    limit: int = Query(...,gt=0)
):
    return await ShippingFetch.search_shipping_city_or_district(q,limit)
