from fastapi import APIRouter, Query, Path, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from controllers.AddressController import AddressFetch, AddressCrud
from controllers.UserController import UserFetch
from schemas.address.AddressSchema import (
    AddressSearchData,
    AddressCreate,
    AddressPaginate,
    AddressData
)
from typing import List

router = APIRouter()

@router.get('/search/city-or-district',response_model=List[AddressSearchData])
async def search_city_or_district(q: str = Query(...,min_length=3,max_length=100)):
    return await AddressFetch.search_city_or_district(q)

@router.post('/create',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully add a new address."}}}
        }
    }
)
async def create_address(address: AddressCreate, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    if user := await UserFetch.filter_by_id(user_id):
        if address.main_address:
            await AddressCrud.check_and_change_main_address_to_false(user_id=user['id'])
        await AddressCrud.create_address(user_id=user['id'],**address.dict())
        return {"detail": "Successfully add a new address."}

@router.get('/my-address',response_model=AddressPaginate)
async def my_address(page: int = Query(...,gt=0), per_page: int = Query(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    if user := await UserFetch.filter_by_id(user_id):
        return await AddressFetch.get_address_by_user_id(user['id'],page=page,per_page=per_page)

@router.get('/my-address/{address_id}',response_model=AddressData,
    responses={
        400: {
            "description": "Address not match with user",
            "content": {"application/json":{"example": {"detail":"Address not match with the current user."}}}
        },
        404: {
            "description": "Address not found",
            "content": {"application/json":{"example": {"detail":"Address not found!"}}}
        }
    }
)
async def my_address_by_id(address_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    if address := await AddressFetch.filter_by_id(address_id):
        user_id = authorize.get_jwt_subject()
        if user := await UserFetch.filter_by_id(user_id):
            if user['id'] != address['user_id']:
                raise HTTPException(status_code=400,detail="Address not match with the current user.")
            return {index:value for index,value in address.items()}
    raise HTTPException(status_code=404,detail="Address not found!")
