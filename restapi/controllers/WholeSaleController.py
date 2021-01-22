import json, uuid
from config import redis_conn, database
from models.WholeSaleModel import wholesale

class WholeSaleCrud:
    @staticmethod
    async def create_wholesale(wholesale_db: list) -> None:
        await database.execute_many(query=wholesale.insert(),values=wholesale_db)

    @staticmethod
    def add_wholesale_to_redis_storage(data_wholesale: dict) -> str:
        ticket = str(uuid.uuid4())
        redis_conn.set(ticket, json.dumps(data_wholesale), 300)  # set expired 5 minutes
        return ticket

class WholeSaleFetch:
    pass
