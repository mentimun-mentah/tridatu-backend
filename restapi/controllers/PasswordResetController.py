from uuid import uuid4
from time import time
from config import database
from sqlalchemy import select
from models.PasswordResetModel import password_reset

class PasswordResetLogic:
    @staticmethod
    def resend_is_expired(resend_expired: int) -> bool:
        return int(time()) > resend_expired

class PasswordResetCrud:
    @staticmethod
    async def create_password_reset(email: str) -> str:
        data = {"id": uuid4().hex, "resend_expired": int(time()) + 300, "email": email}
        await database.execute(query=password_reset.insert(),values=data)
        return data['id']

    @staticmethod
    async def change_resend_expired(id_: str) -> None:
        query = password_reset.update().where(password_reset.c.id == id_)
        await database.execute(query=query,values={"resend_expired": int(time()) + 300})  # add 5 minute expired

class PasswordResetFetch:
    @staticmethod
    async def filter_by_email(email: str) -> password_reset:
        query = select([password_reset]).where(password_reset.c.email == email)
        return await database.fetch_one(query=query)
