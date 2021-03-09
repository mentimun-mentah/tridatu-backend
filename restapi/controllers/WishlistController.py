from config import database
from sqlalchemy.sql import select, exists, func, expression
from models.WishlistModel import wishlist
from models.ProductModel import product
from models.VariantModel import variant
from libs.Pagination import Pagination
from controllers.ProductController import ProductLogic

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
    async def create_wishlist_many(wishlist_db: list) -> None:
        wishlist_db = [
            data for data in wishlist_db
            if await WishlistLogic.check_wishlist(data['product_id'],data['user_id']) is False
        ]
        await database.execute_many(query=wishlist.insert(),values=wishlist_db)

    @staticmethod
    async def delete_wishlist(product_id: int, user_id: int) -> None:
        query = wishlist.delete().where((wishlist.c.product_id == product_id) & (wishlist.c.user_id == user_id))
        await database.execute(query=query)

class WishlistFetch:
    @staticmethod
    async def get_user_wishlist_paginate(user_id: int, **kwargs) -> dict:
        variant_alias = select([
            func.min(variant.c.price).label('min_price'),
            func.max(variant.c.price).label('max_price'),
            func.max(variant.c.discount).label('discount'),
            variant.c.product_id
        ]).group_by(variant.c.product_id).alias('variants')

        wishlist_alias = select([wishlist.join(product.join(variant_alias))]) \
            .where(wishlist.c.user_id == user_id).distinct(wishlist.c.id).apply_labels().alias()

        query = select([wishlist_alias]).where(wishlist_alias.c.products_live == expression.true())

        if q := kwargs['q']:
            query = query.where(wishlist_alias.c.products_name.ilike(f"%{q}%"))
        if kwargs['order_by'] is None:
            query = query.order_by(wishlist_alias.c.wishlists_id.desc())
        if kwargs['order_by'] == 'high_price':
            query = query.order_by(wishlist_alias.c.variants_max_price.desc())
        if kwargs['order_by'] == 'low_price':
            query = query.order_by(wishlist_alias.c.variants_min_price.asc())

        total = await database.execute(query=select([func.count()]).select_from(query.alias()).as_scalar())
        query = query.limit(kwargs['per_page']).offset((kwargs['page'] - 1) * kwargs['per_page'])
        wishlist_db = await database.fetch_all(query=query)

        paginate = Pagination(kwargs['page'], kwargs['per_page'], total, wishlist_db)
        wishlist_data = [{index:value for index,value in item.items()} for item in paginate.items]
        [data.__setitem__('products_wholesale', await ProductLogic.check_wholesale(data['products_id'])) for data in wishlist_data]
        return {
            "data": ProductLogic.set_discount_status(wishlist_data,'products_'),
            "total": paginate.total,
            "next_num": paginate.next_num,
            "prev_num": paginate.prev_num,
            "page": paginate.page,
            "iter_pages": [x for x in paginate.iter_pages()]
        }
