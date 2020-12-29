from fastapi import APIRouter, Query, HTTPException
from controllers.ShippingController import ShippingFetch, ShippingLogic
from schemas.shipping.ShippingSchema import ShippingSearchData, ShippingGetCost, ShippingDataCost
from httpx import AsyncClient
from config import settings
from typing import List

router = APIRouter()

@router.get('/search/city-or-district',response_model=List[ShippingSearchData])
async def search_shipping_city_or_district(
    q: str = Query(...,min_length=1,max_length=100),
    limit: int = Query(...,gt=0)
):
    return await ShippingFetch.search_shipping_city_or_district(q,limit)

@router.post('/get-cost',response_model=ShippingDataCost,
    responses={
        400: {
            "description": "Bad request from rajaongkir",
            "content": {"application/json":{"example": {"detail":"string"}}}
        },
        500: {
            "description": "Internal server error from rajaongkir",
            "content": {"application/json":{"example": {"detail":"Failed to make a request to rajaongkir."}}}
        }
    }
)
async def get_cost_from_courier(cost: ShippingGetCost):
    """
    All the information about rajaongkir:
    - **origin**: ID kota/kabupaten atau kecamatan asal
    - **originType**: Tipe origin: 'city' atau 'subdistrict'
    - **destination**: ID kota/kabupaten atau kecamatan tujuan
    - **destinationType**: Tipe destination: 'city' atau 'subdistrict'
    - **weight**: Berat kiriman dalam gram
    - **courier**: Kode kurir: jne, pos, tiki, rpx, pandu, wahana, sicepat, jnt, pahala, sap, jet,
    indah, dse, slis, first, ncs, star, ninja, lion, idl, rex, ide, sentral

    Note:
    - Courier: Anda juga bisa menggabungkan kurir dengan tanda ":",
    misal **"jne:pos:tiki"** untuk mendapatkan info ongkir ketiga kurir tersebut sekaligus dalam sekali request.
    - Gunakan originType 'city' jika ID yang Anda pakai di 'origin' merupakan ID kota/kabupaten.
    Namun jika Anda menggunakan ID kecamatan pada 'origin' maka gunakan 'subdistrict' pada 'originType'.
    - Gunakan destinationType 'city' jika ID yang Anda pakai di 'destination' merupakan ID kota/kabupaten.
    Namun jika Anda menggunakan ID kecamatan pada 'destination' maka gunakan 'subdistrict' pada 'destinationType'.
    - Penggunaan 'originType' dan 'destinationType' ini sangat berguna jika Anda ingin mengkombinasikan
    pengecekan ongkir. Misal dari 'kota ke kecamatan', 'kecamatan ke kecamatan', atau 'kota ke kota'.
    """
    async with AsyncClient(timeout=None) as client:
        r = await client.post('https://pro.rajaongkir.com/api/cost',
            headers={'key': settings.rajaongkir_key},
            data=cost.dict(exclude_none=True)
        )
        if r.status_code != 200:
            raise HTTPException(status_code=400,detail=r.json()['rajaongkir']['status']['description'])
        try:
            return ShippingLogic.extract_data_from_rajaongkir(r.json())
        except Exception:
            raise HTTPException(status_code=500,detail="Failed to make a request to rajaongkir.")
