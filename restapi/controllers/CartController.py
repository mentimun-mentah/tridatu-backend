from config import database
from sqlalchemy.sql import select, func
from models.CartModel import cart
from models.VariantModel import variant
from models.ProductModel import product
from controllers.WholeSaleController import WholeSaleFetch
from controllers.ProductController import ProductLogic

class CartLogic:
    pass

class CartCrud:
    @staticmethod
    async def create_cart(**kwargs) -> int:
        return await database.execute(query=cart.insert(),values=kwargs)

    @staticmethod
    async def update_cart(id_: int, **kwargs) -> None:
        await database.execute(query=cart.update().where(cart.c.id == id_),values=kwargs)

    @staticmethod
    async def delete_cart(user_id: int, id_: list) -> None:
        await database.execute(query=cart.delete().where((cart.c.id.in_(id_)) & (cart.c.user_id == user_id)))

class CartFetch:
    @staticmethod
    async def get_all_carts(user_id: int, **kwargs) -> list:
        cart_alias = select([cart.join(variant.join(product))]).apply_labels().alias()
        query = select([cart_alias]).where(cart_alias.c.carts_user_id == user_id).order_by(cart_alias.c.carts_id.desc())

        if kwargs['stock'] == 'ready':
            query = query.where(cart_alias.c.variants_stock > 0)
        if kwargs['stock'] == 'empty':
            query = query.where(cart_alias.c.variants_stock < 1)

        cart_db = await database.fetch_all(query=query)
        cart_data = [{index:value for index,value in item.items()} for item in cart_db]
        # set wholesale
        [
            data.__setitem__(
                'products_wholesale',
                await WholeSaleFetch.get_wholesale_filter_by_qty(data['products_id'],data['carts_qty'],include=['min_qty','price'])
            )
            for data in cart_data
        ]

        return ProductLogic.set_discount_status(cart_data,'products_')

    @staticmethod
    async def get_all_carts_from_nav(user_id: int) -> list:
        product_alias = select([
            product.c.id, product.c.name,
            product.c.image_product, product.c.weight
        ]).alias('products')

        variant_alias = select([
            variant.c.id, variant.c.option,
            variant.c.price, variant.c.image,
            variant.c.product_id
        ]).alias('variants')

        cart_alias = select([cart.join(variant_alias.join(product_alias))]).apply_labels().alias()
        query = select([cart_alias]).where(cart_alias.c.carts_user_id == user_id).order_by(cart_alias.c.carts_id.desc())

        cart_db = await database.fetch_all(query=query)
        return [{index:value for index,value in item.items()} for item in cart_db]

    @staticmethod
    async def get_qty_and_item_on_cart(user_id: int) -> dict:
        # count for ready stock item
        variant_alias = select([variant.c.id, variant.c.stock]).where(variant.c.stock > 0).alias('variants')
        cart_alias = select([cart.join(variant_alias)]).where(cart.c.user_id == user_id).apply_labels().alias('carts')

        ready_item = await database.execute(query=select([func.count(cart_alias.c.carts_id)]).as_scalar())
        ready_qty = await database.execute(query=select([func.coalesce(func.sum(cart_alias.c.carts_qty), 0)]).as_scalar())

        # count for empty stock item
        variant_alias = select([variant.c.id, variant.c.stock]).where(variant.c.stock < 1).alias('variants')
        cart_alias = select([cart.join(variant_alias)]).where(cart.c.user_id == user_id).apply_labels().alias('carts')

        empty_item = await database.execute(query=select([func.count(cart_alias.c.carts_id)]).as_scalar())
        empty_qty = await database.execute(query=select([func.coalesce(func.sum(cart_alias.c.carts_qty), 0)]).as_scalar())

        # count all item
        cart_alias = select([cart]).where(cart.c.user_id == user_id).apply_labels().alias('carts')
        total_item = await database.execute(query=select([func.count(cart_alias.c.carts_id)]).as_scalar())
        total_qty = await database.execute(query=select([func.coalesce(func.sum(cart_alias.c.carts_qty), 0)]).as_scalar())

        return {
            'user_id': user_id,
            'total_item': total_item,
            'total_qty': total_qty,
            'ready_stock': {
                'total_item': ready_item,
                'total_qty': ready_qty
            },
            'empty_stock': {
                'total_item': empty_item,
                'total_qty': empty_qty
            }
        }

    @staticmethod
    async def get_all_carts_product_id(user_id: int, id_: list) -> list:
        variant_alias = select([variant.c.id, variant.c.product_id]).alias('variants')
        cart_alias = select([cart.join(variant_alias)]).apply_labels().alias('carts')

        query = select([cart_alias]).distinct(cart_alias.c.variants_product_id) \
            .where((cart_alias.c.carts_id.in_(id_)) & (cart_alias.c.carts_user_id == user_id))

        cart_db = await database.fetch_all(query=query)
        return [item['variants_product_id'] for item in cart_db]

    @staticmethod
    async def filter_by_user_variant(user_id: int, variant_id: int) -> cart:
        query = select([cart]).where((cart.c.user_id == user_id) & (cart.c.variant_id == variant_id))
        return await database.fetch_one(query=query)
