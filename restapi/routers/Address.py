from fastapi import APIRouter, Query, Path, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from controllers.AddressController import AddressFetch, AddressCrud
from controllers.UserController import UserFetch
from schemas.address.AddressSchema import (
    AddressSearchData,
    AddressCreateUpdate,
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
async def create_address(address: AddressCreateUpdate, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    if user := await UserFetch.filter_by_id(user_id):
        data = address.dict()
        if not await AddressFetch.check_main_address_true_in_db(user['id']):
            data.update({"main_address": True})
        await AddressCrud.create_address(user_id=user['id'],**data)
        return {"detail": "Successfully add a new address."}

@router.get('/my-address',response_model=AddressPaginate)
async def my_address(page: int = Query(...,gt=0), per_page: int = Query(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = authorize.get_jwt_subject()
    if user := await UserFetch.filter_by_id(user_id):
        return await AddressFetch.get_all_address_by_user_id(user['id'],page=page,per_page=per_page)

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

@router.put('/update/{address_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully update the address."}}}
        },
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
async def update_address(
    address_data: AddressCreateUpdate,
    address_id: int = Path(...,gt=0),
    authorize: AuthJWT = Depends()
):
    authorize.jwt_required()

    if address := await AddressFetch.filter_by_id(address_id):
        user_id = authorize.get_jwt_subject()
        if user := await UserFetch.filter_by_id(user_id):
            if user['id'] != address['user_id']:
                raise HTTPException(status_code=400,detail="Address not match with the current user.")
            # update address
            await AddressCrud.update_address(address['id'],**address_data.dict())
            return {"detail": "Successfully update the address."}

    raise HTTPException(status_code=404,detail="Address not found!")

@router.put('/main-address-true/{address_id}',
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"detail":"Successfully set the address to main address."}}}
        },
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
async def main_address_true(address_id: int = Path(...,gt=0), authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    if address := await AddressFetch.filter_by_id(address_id):
        user_id = authorize.get_jwt_subject()
        if user := await UserFetch.filter_by_id(user_id):
            if user['id'] != address['user_id']:
                raise HTTPException(status_code=400,detail="Address not match with the current user.")
            # change address to main address
            await AddressCrud.change_all_main_address_to_false(user['id'])
            await AddressCrud.change_address_to_main_address(address['id'])
            return {"detail": "Successfully set the address to main address."}
    raise HTTPException(status_code=404,detail="Address not found!")
