import os, bcrypt, httpx
from PIL import Image
from io import BytesIO
from uuid import uuid4
from config import database
from sqlalchemy import select, func
from models.UserModel import user

dir_avatars = os.path.join(os.path.dirname(__file__),'../static/avatars/')

class UserLogic:
    @staticmethod
    def password_is_same_as_hash(password: str, password_db: str) -> bool:
        return bcrypt.checkpw(password.encode(),password_db.encode())

class UserCrud:
    @staticmethod
    async def create_user(**kwargs) -> int:
        hashed_pass = bcrypt.hashpw(kwargs['password'].encode(), bcrypt.gensalt())
        kwargs.update({'password': hashed_pass.decode('utf-8')})
        return await database.execute(query=user.insert(),values=kwargs)

    @staticmethod
    async def save_user_from_oauth(**kwargs) -> int:
        # get image from url
        async with httpx.AsyncClient() as client:
            r = await client.get(kwargs['avatar'])
            # save image to directory
            with Image.open(BytesIO(r.content)) as im:
                ext = im.format.lower()
                filename = uuid4().hex + f'.{ext}'
                im.save(os.path.join(dir_avatars,filename))

        # save to db
        kwargs.update({'avatar': filename})
        return await database.execute(query=user.insert(),values=kwargs)

    @staticmethod
    async def update_password_user(id_: int, password: str) -> None:
        query = user.update().where(user.c.id == id_)
        hashed_pass = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        await database.execute(query=query,values={
            "password": hashed_pass.decode('utf-8'),
            "updated_at": func.now()
        })

class UserFetch:
    @staticmethod
    async def filter_by_email(email: str) -> user:
        query = select([user]).where(user.c.email == email)
        return await database.fetch_one(query=query)

    @staticmethod
    async def filter_by_id(id_: int) -> user:
        query = select([user]).where(user.c.id == id_)
        return await database.fetch_one(query=query)
