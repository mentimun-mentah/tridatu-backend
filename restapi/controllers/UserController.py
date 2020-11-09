import bcrypt
from config import database
from sqlalchemy import select
from models.UserModel import users

class UserLogic:
    @staticmethod
    def password_is_same_as_hash(password: str, password_db: str) -> bool:
        return bcrypt.checkpw(password.encode(),password_db.encode())

class UserCrud:
    @staticmethod
    async def create_user(**kwargs) -> int:
        hashed_pass = bcrypt.hashpw(kwargs['password'].encode(), bcrypt.gensalt())
        kwargs.update({'password': hashed_pass.decode('utf-8')})
        return await database.execute(query=users.insert(),values=kwargs)

class UserFetch:
    @staticmethod
    async def filter_by_email(email: str) -> users:
        query = select([users]).where(users.c.email == email)
        return await database.fetch_one(query=query)

    @staticmethod
    async def filter_by_id(id_: int) -> users:
        query = select([users]).where(users.c.id == id_)
        return await database.fetch_one(query=query)
