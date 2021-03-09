from config import database
from sqlalchemy.sql import select
from models.PromoModel import promo
from datetime import datetime
from pytz import timezone
from config import settings

tz = timezone(settings.timezone)

class PromoLogic:
    @staticmethod
    def set_period_status(promo_data: list, key: str = '') -> list:
        for data in promo_data:
            # not active
            if data[f'{key}period_start'] is None and data[f'{key}period_end'] is None:
                data.update({f'{key}period_status': 'not_active'})
            else:
                period_start = tz.localize(data[f'{key}period_start'])
                period_end = tz.localize(data[f'{key}period_end'])
                time_now = datetime.now(tz)
                # ongoing
                if time_now > period_start and time_now < period_end:
                    data.update({f'{key}period_status': 'ongoing'})
                # will come
                elif time_now < period_start:
                    data.update({f'{key}period_status': 'will_come'})
                # have ended
                elif time_now > period_end:
                    data.update({f'{key}period_status': 'have_ended'})

        return promo_data

class PromoCrud:
    @staticmethod
    async def create_promo(**kwargs) -> int:
        return await database.execute(promo.insert(),values=kwargs)

    @staticmethod
    async def update_promo(id_: int, **kwargs) -> None:
        await database.execute(query=promo.update().where(promo.c.id == id_),values=kwargs)

    @staticmethod
    async def delete_promo(id_: int) -> None:
        await database.execute(query=promo.delete().where(promo.c.id == id_))

class PromoFetch:
    @staticmethod
    async def filter_by_slug(slug: str) -> promo:
        query = select([promo]).where(promo.c.slug == slug)
        return await database.fetch_one(query=query)

    @staticmethod
    async def filter_by_id(id_: int) -> promo:
        query = select([promo]).where(promo.c.id == id_)
        return await database.fetch_one(query=query)
