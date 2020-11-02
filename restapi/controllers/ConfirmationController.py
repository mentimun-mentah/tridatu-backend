from uuid import uuid4
from config import database
from sqlalchemy import select
from models.ConfirmationModel import confirmation

class ConfirmationCrud:
    async def create_confirmation(user_id: int) -> str:
        data = {"id": uuid4().hex, "user_id": user_id}
        await database.execute(query=confirmation.insert(), values=data)
        return data["id"]

    async def user_activated(token: str) -> None:
        query = confirmation.update().where(confirmation.c.id == token)
        return await database.execute(query=query, values={"activated": True})

class ConfirmationFetch:
    async def filter_by_id(token: str) -> confirmation:
        query = select([confirmation]).where(confirmation.c.id == token)
        return await database.fetch_one(query=query)
