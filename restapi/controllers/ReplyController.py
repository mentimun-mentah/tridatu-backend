from config import database
from sqlalchemy.sql import select
from models.ReplyModel import reply
from models.UserModel import user
from typing import Union

class ReplyCrud:
    @staticmethod
    async def create_reply(**kwargs) -> int:
        return await database.execute(reply.insert(),values=kwargs)

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
