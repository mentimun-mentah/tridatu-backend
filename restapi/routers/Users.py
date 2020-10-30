from fastapi import APIRouter, HTTPException
from controllers.UserController import UserCrud, UserFetch
from schemas.users.RegisterSchema import RegisterSchema

router = APIRouter()

@router.post('/register',status_code=201)
async def register(user: RegisterSchema):
    if await UserFetch.filter_by_email(email=user.email):
        raise HTTPException(status_code=422,detail="The email has already been taken.")

    await UserCrud.create_user(**user.dict(exclude={'confirm_password'}))
    return {"detail":"Check your email to activated user."}
