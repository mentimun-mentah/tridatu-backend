from config import redis_conn, database
from fastapi.requests import Request
from user_agents import parse
from sqlalchemy import Table

class Visitor:
    def __init__(self,request: Request):
        self.request = request
        self.seconds = 15

    async def increment_visitor(self,table: Table, id_: int) -> None:
        ip = self.request.client.host
        path = self.request.url.path
        user_agent = parse(self.request.headers.get('user-agent'))
        is_bot = user_agent.is_bot
        user_agent = str(user_agent)

        # check if visitor is not localhost,crawler/bot and not exists in redis
        if(
            ip != '127.0.0.1' and
            is_bot is False and
            redis_conn.get(f"{ip}:{path}:{user_agent}") is None
        ):
            await database.execute(
                query=table.update().where(table.c.id == id_),
                values={'visitor': table.c.visitor + 1}
            )

            # for delay increment visitor and avoid refresh page immediately
            redis_conn.set(f"{ip}:{path}:{user_agent}", "true", self.seconds)
