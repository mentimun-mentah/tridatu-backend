from config import database
from sqlalchemy.sql import select, func
from models.CommentModel import comment
from models.UserModel import user
from libs.Pagination import Pagination

class CommentCrud:
    @staticmethod
    async def create_comment(**kwargs) -> int:
        return await database.execute(comment.insert(),values=kwargs)

class CommentFetch:
    @staticmethod
    async def get_all_comments_paginate(**kwargs) -> dict:
        query = select([comment.join(user)]) \
            .where((comment.c.comment_id == kwargs['comment_id']) & (comment.c.comment_type == kwargs['comment_type'])) \
            .order_by(comment.c.id.desc()).apply_labels()

        total = await database.execute(query=select([func.count()]).select_from(query.alias()).as_scalar())
        query = query.limit(kwargs['per_page']).offset((kwargs['page'] - 1) * kwargs['per_page'])
        comment_db = await database.fetch_all(query=query)

        paginate = Pagination(kwargs['page'], kwargs['per_page'], total, comment_db)
        return {
            "data": [{index:value for index,value in item.items()} for item in paginate.items],
            "total": paginate.total,
            "next_num": paginate.next_num,
            "prev_num": paginate.prev_num,
            "page": paginate.page,
            "iter_pages": [x for x in paginate.iter_pages()]
        }
