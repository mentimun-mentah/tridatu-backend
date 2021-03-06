from config import database
from sqlalchemy.sql import select
from models.PromoModel import promo

class PromoLogic:
    pass

class PromoCrud:
    @staticmethod
    async def create_promo(**kwargs) -> int:
        return await database.execute(promo.insert(),values=kwargs)

class PromoFetch:
    @staticmethod
    async def filter_by_slug(slug: str) -> promo:
        query = select([promo]).where(promo.c.slug == slug)
        return await database.fetch_one(query=query)
