from config import database
from sqlalchemy.sql import select
from models.BrandModel import brand

class BrandLogic:
    pass

class BrandCrud:
    async def create_brand(name: str, image: str) -> int:
        return await database.execute(query=brand.insert(),values={"name_brand": name, "image_brand": image})

class BrandFetch:
    async def filter_by_name(name: str) -> brand:
        query = select([brand]).where(brand.c.name_brand == name)
        return await database.fetch_one(query=query)
