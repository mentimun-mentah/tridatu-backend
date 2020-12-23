from config import database
from sqlalchemy.sql import select, exists, func, expression
from models.WishlistModel import wishlist
from models.ProductModel import product
from models.VariantModel import variant
from libs.Pagination import Pagination

class WishlistLogic:
    @staticmethod
    async def check_wishlist(product_id: int, user_id: int) -> bool:
        query = select([exists().where((wishlist.c.product_id == product_id) & (wishlist.c.user_id == user_id))]) \
            .as_scalar()
        return await database.execute(query=query)

class WishlistCrud:
    @staticmethod
    async def create_wishlist(product_id: int, user_id: int) -> int:
        return await database.execute(wishlist.insert(),values={'product_id': product_id, 'user_id': user_id})

    @staticmethod
    async def delete_wishlist(product_id: int, user_id: int) -> None:
        query = wishlist.delete().where((wishlist.c.product_id == product_id) & (wishlist.c.user_id == user_id))
        await database.execute(query=query)

class WishlistFetch:
    @staticmethod
    async def get_user_wishlist_paginate(user_id: int, **kwargs) -> dict:
        wishlist_alias = select([wishlist.join(product.join(variant))]) \
            .where(wishlist.c.user_id == user_id).distinct(wishlist.c.id).apply_labels().alias()

        query = select([wishlist_alias])
        query = query.where(wishlist_alias.c.products_live == expression.true())

        if q := kwargs['q']:
            query = query.where(wishlist_alias.c.products_name.ilike(f"%{q}%"))
        if kwargs['order_by'] is None:
            query = query.order_by(wishlist_alias.c.wishlists_id.desc())
        if kwargs['order_by'] == 'high_price':
            query = query.order_by(wishlist_alias.c.variants_price.desc())
        if kwargs['order_by'] == 'low_price':
            query = query.order_by(wishlist_alias.c.variants_price.asc())

        total = await database.execute(query=select([func.count()]).select_from(query.alias()).as_scalar())
        query = query.limit(kwargs['per_page']).offset((kwargs['page'] - 1) * kwargs['per_page'])
        wishlist_db = await database.fetch_all(query=query)

        paginate = Pagination(kwargs['page'], kwargs['per_page'], total, wishlist_db)
        return {
            "data": [{index:value for index,value in item.items()} for item in paginate.items],
            "total": paginate.total,
            "next_num": paginate.next_num,
            "prev_num": paginate.prev_num,
            "page": paginate.page,
            "iter_pages": [x for x in paginate.iter_pages()]
        }
