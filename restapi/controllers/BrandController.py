from config import database
from sqlalchemy.sql import select
from models.BrandModel import brand

class BrandLogic:
    pass

class BrandCrud:
    async def create_brand(name: str, image: str) -> int:
        return await database.execute(query=brand.insert(),values={"name_brand": name, "image_brand": image})

    async def update_brand(id_: int, **kwargs) -> None:
        await database.execute(query=brand.update().where(brand.c.id_brand == id_),values=kwargs)

    async def delete_brand(id_: int) -> None:
        await database.execute(query=brand.delete().where(brand.c.id_brand == id_))

class BrandFetch:
    async def get_all_brands() -> brand:
        return await database.fetch_all(query=select([brand]))

    async def filter_by_name(name: str) -> brand:
        query = select([brand]).where(brand.c.name_brand == name)
        return await database.fetch_one(query=query)

    async def filter_by_id(id_: int) -> brand:
        query = select([brand]).where(brand.c.id_brand == id_)
        return await database.fetch_one(query=query)
