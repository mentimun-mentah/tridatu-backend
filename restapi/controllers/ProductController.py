from config import database
from sqlalchemy.sql import select, func
from models.ProductModel import product
from models.VariantModel import variant
from libs.Pagination import Pagination

class ProductLogic:
    pass

class ProductCrud:
    @staticmethod
    async def create_product(**kwargs) -> int:
        return await database.execute(product.insert(),values=kwargs)

class ProductFetch:
    @staticmethod
    async def get_all_products_paginate(**kwargs) -> dict:
        product_alias = select([product.join(variant)]).distinct(product.c.id_product).alias()

        query = select([product_alias]).where(product_alias.c.live_product == kwargs['live'])

        if q := kwargs['q']:
            query = query.where(product_alias.c.name_product.ilike(f"%{q}%"))
        if kwargs['order_by'] == 'high_price':
            query = query.order_by(product_alias.c.price_variant.desc())
        if kwargs['order_by'] == 'low_price':
            query = query.order_by(product_alias.c.price_variant.asc())
        if (p_min := kwargs['p_min']) and (p_max := kwargs['p_max']):
            query = query.where((product_alias.c.price_variant >= p_min) & (product_alias.c.price_variant <= p_max))
        if (p_min := kwargs['p_min']) and not kwargs['p_max']:
            query = query.where(product_alias.c.price_variant >= p_min)
        if (p_max := kwargs['p_max']) and not kwargs['p_min']:
            query = query.where(product_alias.c.price_variant <= p_max)
        if item_sub_cat := kwargs['item_sub_cat']:
            query = query.where(product_alias.c.item_sub_category_id.in_(item_sub_cat))
        if brand := kwargs['brand']:
            query = query.where(product_alias.c.brand_id.in_(brand))
        if kwargs['pre_order'] is not None:
            if kwargs['pre_order'] is True:
                query = query.where(product_alias.c.preorder_product.isnot(None))
            if kwargs['pre_order'] is False:
                query = query.where(product_alias.c.preorder_product.is_(None))
        if kwargs['condition'] is not None:
            query = query.where(product_alias.c.condition_product == kwargs['condition'])

        total = await database.execute(query=select([func.count()]).select_from(query.alias()).as_scalar())
        query = query.limit(kwargs['per_page']).offset((kwargs['page'] - 1) * kwargs['per_page'])
        product_db = await database.fetch_all(query=query)

        paginate = Pagination(kwargs['page'], kwargs['per_page'], total, product_db)
        return {
            "data": [{index:value for index,value in item.items()} for item in paginate.items],
            "total": paginate.total,
            "next_num": paginate.next_num,
            "prev_num": paginate.prev_num,
            "page": paginate.page,
            "iter_pages": [x for x in paginate.iter_pages()]
        }

    @staticmethod
    async def filter_by_slug(slug: str) -> product:
        query = select([product]).where(product.c.slug_product == slug)
        return await database.fetch_one(query=query)
