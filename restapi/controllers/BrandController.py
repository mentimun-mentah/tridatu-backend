from config import database
from sqlalchemy.sql import select
from models.BrandModel import brand

class BrandLogic:
    pass

class BrandCrud:
    @staticmethod
    async def create_brand(name: str, image: str) -> int:
        return await database.execute(query=brand.insert(),values={"name": name, "image": image})

    @staticmethod
    async def update_brand(id_: int, **kwargs) -> None:
        await database.execute(query=brand.update().where(brand.c.id == id_),values=kwargs)

    @staticmethod
    async def delete_brand(id_: int) -> None:
        await database.execute(query=brand.delete().where(brand.c.id == id_))

class BrandFetch:
    @staticmethod
    async def get_all_brands() -> brand:
        return await database.fetch_all(query=select([brand]))

    @staticmethod
    async def filter_by_name(name: str) -> brand:
        query = select([brand]).where(brand.c.name == name)
        return await database.fetch_one(query=query)

    @staticmethod
    async def filter_by_id(id_: int) -> brand:
        query = select([brand]).where(brand.c.id == id_)
        return await database.fetch_one(query=query)
