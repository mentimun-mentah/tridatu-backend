from uuid import uuid4
from time import time
from config import database
from sqlalchemy import select
from models.ConfirmationModel import confirmation

class ConfirmationLogic:
    @staticmethod
    def resend_is_expired(resend_expired: int) -> bool:
        return int(time()) > resend_expired

    @staticmethod
    async def generate_resend_expired(confirm_id: int) -> None:
        query = confirmation.update().where(confirmation.c.id == confirm_id)
        return await database.execute(query=query,values={"resend_expired": int(time() + 300)})  # add 5 minutes

class ConfirmationCrud:
    @staticmethod
    async def create_confirmation(user_id: int) -> str:
        data = {"id": uuid4().hex, "user_id": user_id}
        await database.execute(query=confirmation.insert(), values=data)
        return data["id"]

    @staticmethod
    async def user_activated(token: str) -> None:
        query = confirmation.update().where(confirmation.c.id == token)
        return await database.execute(query=query, values={"activated": True})

class ConfirmationFetch:
    @staticmethod
    async def filter_by_id(token: str) -> confirmation:
        query = select([confirmation]).where(confirmation.c.id == token)
        return await database.fetch_one(query=query)

    @staticmethod
    async def filter_by_user_id(user_id: int) -> confirmation:
        query = select([confirmation]).where(confirmation.c.user_id == user_id)
        return await database.fetch_one(query=query)
