from config import database
from sqlalchemy.sql import select
from models.OutletModel import outlet

class OutletLogic:
    pass

class OutletCrud:
    async def create_outlet(image: str) -> int:
        return await database.execute(query=outlet.insert(),values={'image': image})

    async def delete_outlet(id_: int) -> None:
        return await database.execute(query=outlet.delete().where(outlet.c.id == id_))

class OutletFetch:
    async def get_all_outlets() -> outlet:
        return await database.fetch_all(query=select([outlet]))

    async def filter_by_id(id_: int) -> outlet:
        query = select([outlet]).where(outlet.c.id == id_)
        return await database.fetch_one(query=query)
