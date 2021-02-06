from config import database
from sqlalchemy.sql import select, func
from models.CommentModel import comment
from models.ReplyModel import reply
from models.UserModel import user
from libs.Pagination import Pagination

class CommentLogic:
    @staticmethod
    async def count_total_replies(comment_id: int) -> int:
        query = select([func.count(reply.c.id)]).where(reply.c.comment_id == comment_id).as_scalar()
        return await database.execute(query=query)

class CommentCrud:
    @staticmethod
    async def create_comment(**kwargs) -> int:
        return await database.execute(comment.insert(),values=kwargs)

    @staticmethod
    async def delete_comment(id_: int) -> None:
        await database.execute(query=comment.delete().where(comment.c.id == id_))

class CommentFetch:
    @staticmethod
    async def get_all_comments_paginate(**kwargs) -> dict:
        query = select([comment.join(user)]) \
            .where(
                (comment.c.commentable_id == kwargs['commentable_id']) &
                (comment.c.commentable_type == kwargs['commentable_type'])) \
            .order_by(comment.c.id.desc()).apply_labels()

        total = await database.execute(query=select([func.count()]).select_from(query.alias()).as_scalar())
        query = query.limit(kwargs['per_page']).offset((kwargs['page'] - 1) * kwargs['per_page'])
        comment_db = await database.fetch_all(query=query)

        paginate = Pagination(kwargs['page'], kwargs['per_page'], total, comment_db)
        paginate_data = [{index:value for index,value in item.items()} for item in paginate.items]
        # count total replies on comment
        [
            data.__setitem__('total_replies', await CommentLogic.count_total_replies(data['comments_id']))
            for data in paginate_data
        ]
        return {
            "data": paginate_data,
            "total": paginate.total,
            "next_num": paginate.next_num,
            "prev_num": paginate.prev_num,
            "page": paginate.page,
            "iter_pages": [x for x in paginate.iter_pages()]
        }

    @staticmethod
    async def filter_by_id(id_: int) -> comment:
        query = select([comment]).where(comment.c.id == id_)
        return await database.fetch_one(query=query)
