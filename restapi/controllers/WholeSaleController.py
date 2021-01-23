import json, uuid
from config import redis_conn, database
from sqlalchemy.sql import select
from models.WholeSaleModel import wholesale

class WholeSaleCrud:
    @staticmethod
    async def create_wholesale(wholesale_db: list) -> None:
        await database.execute_many(query=wholesale.insert(),values=wholesale_db)

    @staticmethod
    async def delete_wholesale(product_id: int) -> None:
        await database.execute(query=wholesale.delete().where(wholesale.c.product_id == product_id))

    @staticmethod
    def add_wholesale_to_redis_storage(data_wholesale: dict) -> str:
        ticket = str(uuid.uuid4())
        redis_conn.set(ticket, json.dumps(data_wholesale), 300)  # set expired 5 minutes
        return ticket

class WholeSaleFetch:
    @staticmethod
    async def get_wholesale_by_product_id(product_id: int, exclude: list = []) -> list:
        wholesale_db = await database.fetch_all(query=select([wholesale]).where(wholesale.c.product_id == product_id))
        return [{index:value for index,value in item.items() if index not in exclude} for item in wholesale_db]
