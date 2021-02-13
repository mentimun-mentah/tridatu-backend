from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT
from controllers.WholeSaleController import WholeSaleCrud
from controllers.UserController import UserFetch
from schemas.wholesale.WholeSaleSchema import WholeSaleCreateUpdate

router = APIRouter()

@router.post('/create-ticket',status_code=201,
    responses={
        201: {
            "description": "Successful Response",
            "content": {"application/json":{"example": {"ticket":"unique string"}}}
        },
        401: {
            "description": "User without role admin",
            "content": {"application/json": {"example":{"detail":"Only users with admin privileges can do this action."}}}
        },
    }
)
async def add_wholesale_to_temp_storage(wholesale_data: WholeSaleCreateUpdate, authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    user_id = int(authorize.get_jwt_subject())
    await UserFetch.user_is_admin(user_id)

    ticket = WholeSaleCrud.add_wholesale_to_redis_storage(wholesale_data.dict(exclude={'variant'}))
    return {"ticket": ticket}
