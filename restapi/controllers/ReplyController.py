from config import database
from sqlalchemy.sql import select
from models.ReplyModel import reply
from models.UserModel import user
from typing import Union

class ReplyCrud:
    @staticmethod
    async def create_reply(**kwargs) -> int:
        return await database.execute(reply.insert(),values=kwargs)

    @staticmethod
    async def delete_reply(id_: int) -> None:
        await database.execute(query=reply.delete().where(reply.c.id == id_))

class ReplyFetch:
    @staticmethod
    async def get_all_replies_in_comment(comment_id: list) -> Union[list,dict]:
        if comment_id is None: return []

        if len(comment_id) > 1:
            results = list()

            for id_ in comment_id:
                query = select([reply.join(user)]).where(reply.c.comment_id == id_) \
                    .order_by(reply.c.id.desc()).limit(2).apply_labels()
                reply_db = await database.fetch_all(query=query)
                reply_data = [{index:value for index,value in item.items()} for item in reply_db]

                results.append({
                    'comments_id': id_,
                    'comments_replies': reply_data[::-1]
                })

            return results
        else:
            query = select([reply.join(user)]).where(reply.c.comment_id == comment_id[0]).apply_labels()
            reply_db = await database.fetch_all(query=query)
            reply_data = [{index:value for index,value in item.items()} for item in reply_db]

            return {'comments_id': comment_id[0], 'comments_replies': reply_data}

    @staticmethod
    async def filter_by_id(id_: int) -> reply:
        query = select([reply]).where(reply.c.id == id_)
        return await database.fetch_one(query=query)
