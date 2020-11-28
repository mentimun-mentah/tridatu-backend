from config import database
from sqlalchemy.sql import select
from models.ProductModel import product

class ProductLogic:
    pass

class ProductCrud:
    async def create_product(**kwargs) -> int:
        return await database.execute(product.insert(),values=kwargs)

class ProductFetch:
    async def filter_by_slug(slug: str) -> product:
        query = select([product]).where(product.c.slug_product == slug)
        return await database.fetch_one(query=query)
