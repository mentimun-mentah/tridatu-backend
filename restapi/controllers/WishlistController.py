from config import database
from sqlalchemy.sql import select, exists
from models.WishlistModel import wishlist

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
    pass
