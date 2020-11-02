import bcrypt
from config import database
from sqlalchemy import select
from models.UserModel import users

class UserLogic:
    pass

class UserCrud:
    async def create_user(**kwargs) -> int:
        hashed_pass = bcrypt.hashpw(kwargs['password'].encode(), bcrypt.gensalt())
        kwargs.update({'password': hashed_pass.decode('utf-8')})
        return await database.execute(query=users.insert(),values=kwargs)

class UserFetch:
    async def filter_by_email(email: str) -> users:
        query = select([users]).where(users.c.email == email)
        return await database.fetch_one(query=query)

    async def filter_by_id(id_: int) -> users:
        query = select([users]).where(users.c.id == id_)
        return await database.fetch_one(query=query)
