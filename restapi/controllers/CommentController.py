from config import database
from models.CommentModel import comment

class CommentCrud:
    @staticmethod
    async def create_comment(**kwargs) -> int:
        return await database.execute(comment.insert(),values=kwargs)

class CommentFetch:
    pass
