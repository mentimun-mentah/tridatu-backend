from config import database
from models.ReplyModel import reply

class ReplyCrud:
    @staticmethod
    async def create_reply(**kwargs) -> int:
        return await database.execute(reply.insert(),values=kwargs)

class ReplyFetch:
    pass
