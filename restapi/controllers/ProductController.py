from config import database
from sqlalchemy import true
from sqlalchemy.sql import select, func, exists
from models.BrandModel import brand
from models.ProductModel import product
from models.VariantModel import variant
from models.WholeSaleModel import wholesale
from models.CategoryModel import category
from models.SubCategoryModel import sub_category
from models.ItemSubCategoryModel import item_sub_category
from controllers.VariantController import VariantFetch
from libs.Pagination import Pagination
from datetime import datetime
from pytz import timezone
from config import settings

tz = timezone(settings.timezone)

class ProductLogic:
    @staticmethod
    async def check_wholesale(product_id: int) -> bool:
        query = select([exists().where(wholesale.c.product_id == product_id)]).as_scalar()
        return await database.execute(query=query)

    @staticmethod
    def set_discount_status(product_data: list, key: str = '') -> list:
        for data in product_data:
            # not active
            if data[f'{key}discount_start'] is None and data[f'{key}discount_end'] is None:
                data.update({f'{key}discount_status': 'not_active'})
            else:
                discount_start = tz.localize(data[f'{key}discount_start'])
                discount_end = tz.localize(data[f'{key}discount_end'])
                time_now = datetime.now(tz)
                # ongoing
                if time_now > discount_start and time_now < discount_end:
                    data.update({f'{key}discount_status': 'ongoing'})
                # will come
                elif time_now < discount_start:
                    data.update({f'{key}discount_status': 'will_come'})
                # have ended
                elif time_now > discount_end:
                    data.update({f'{key}discount_status': 'have_ended'})

        return product_data

class ProductCrud:
    @staticmethod
    async def create_product(**kwargs) -> int:
        return await database.execute(product.insert(),values=kwargs)

    @staticmethod
    async def update_product(id_: int, **kwargs) -> None:
        kwargs.update({"updated_at": func.now()})
        await database.execute(query=product.update().where(product.c.id == id_),values=kwargs)

    @staticmethod
    async def delete_product(id_: int) -> None:
        await database.execute(query=product.delete().where(product.c.id == id_))

    @staticmethod
    async def change_product_alive_archive(id_: int, live: bool) -> None:
        query = product.update().where(product.c.id == id_)
        await database.execute(query=query,values={'live': not live, 'updated_at': func.now()})

class ProductFetch:
    @staticmethod
    async def search_products_by_name(q: str, limit: int) -> list:
        query = select([product]).where((product.c.name.ilike(f"%{q}%")) & (product.c.live == true())).limit(limit)
        product_db = await database.fetch_all(query=query)
        return [
            {'value':value for index,value in item.items() if index == 'name'} for item in product_db
        ]

    @staticmethod
    async def get_product_recommendation(limit: int) -> list:
        product_alias = select([product.join(variant)]).distinct(product.c.id).apply_labels().alias()

        query = select([product_alias]).where(product_alias.c.products_live == true()) \
            .order_by(func.random()).limit(limit)

        product_db = await database.fetch_all(query=query)
        product_data = [{index:value for index,value in item.items()} for item in product_db]
        [data.__setitem__('products_wholesale', await ProductLogic.check_wholesale(data['products_id'])) for data in product_data]

        return product_data

    @staticmethod
    async def get_all_discounts_paginate(**kwargs) -> dict:
        variant_alias = select([
            func.min(variant.c.price).label('min_price'),
            func.max(variant.c.price).label('max_price'),
            func.max(variant.c.discount).label('discount'),
            variant.c.product_id
        ]).group_by(variant.c.product_id).alias('variants')
        product_alias = select([product.join(variant_alias)]).distinct(product.c.id).apply_labels().alias()

        query = select([product_alias]).where(product_alias.c.products_live == true()).order_by(product_alias.c.products_updated_at.desc())

        time_now = datetime.now(tz).replace(tzinfo=None)
        if q := kwargs['q']:
            query = query.where(product_alias.c.products_name.ilike(f"%{q}%"))
        if kwargs['status'] == 'not_active':
            query = query.where((product_alias.c.products_discount_start.is_(None)) & ((product_alias.c.products_discount_end.is_(None))))
        if kwargs['status'] == 'ongoing':
            query = query.where((time_now > product_alias.c.products_discount_start) & (time_now < product_alias.c.products_discount_end))
        if kwargs['status'] == 'will_come':
            query = query.where(time_now < product_alias.c.products_discount_start)
        if kwargs['status'] == 'have_ended':
            query = query.where(time_now > product_alias.c.products_discount_end)

        total = await database.execute(query=select([func.count()]).select_from(query.alias()).as_scalar())
        query = query.limit(kwargs['per_page']).offset((kwargs['page'] - 1) * kwargs['per_page'])
        product_db = await database.fetch_all(query=query)

        paginate = Pagination(kwargs['page'], kwargs['per_page'], total, product_db)
        product_data = [{index:value for index,value in item.items()} for item in paginate.items]
        return {
            "data": ProductLogic.set_discount_status(product_data,'products_'),
            "total": paginate.total,
            "next_num": paginate.next_num,
            "prev_num": paginate.prev_num,
            "page": paginate.page,
            "iter_pages": [x for x in paginate.iter_pages()]
        }

    @staticmethod
    async def get_all_products_paginate(**kwargs) -> dict:
        product_alias = select([product.join(variant)]).distinct(product.c.id).apply_labels().alias()

        query = select([product_alias])

        if kwargs['live'] is not None:
            query = query.where(product_alias.c.products_live == kwargs['live'])
        if q := kwargs['q']:
            query = query.where(product_alias.c.products_name.ilike(f"%{q}%"))
        if kwargs['order_by'] == 'high_price':
            query = query.order_by(product_alias.c.variants_price.desc())
        if kwargs['order_by'] == 'low_price':
            query = query.order_by(product_alias.c.variants_price.asc())
        if kwargs['order_by'] == 'newest':
            query = query.order_by(product_alias.c.products_id.desc())
        if kwargs['order_by'] == 'visitor':
            query = query.order_by(product_alias.c.products_visitor.desc())
        if (p_min := kwargs['p_min']) and (p_max := kwargs['p_max']):
            query = query.where((product_alias.c.variants_price >= p_min) & (product_alias.c.variants_price <= p_max))
        if (p_min := kwargs['p_min']) and not kwargs['p_max']:
            query = query.where(product_alias.c.variants_price >= p_min)
        if (p_max := kwargs['p_max']) and not kwargs['p_min']:
            query = query.where(product_alias.c.variants_price <= p_max)
        if item_sub_cat := kwargs['item_sub_cat']:
            query = query.where(product_alias.c.products_item_sub_category_id.in_(item_sub_cat))
        if brand := kwargs['brand']:
            query = query.where(product_alias.c.products_brand_id.in_(brand))
        if kwargs['pre_order'] is not None:
            if kwargs['pre_order'] is True:
                query = query.where(product_alias.c.products_preorder.isnot(None))
            if kwargs['pre_order'] is False:
                query = query.where(product_alias.c.products_preorder.is_(None))
        if kwargs['condition'] is not None:
            query = query.where(product_alias.c.products_condition == kwargs['condition'])
        if kwargs['wholesale'] is True:
            query = query.where(product_alias.c.products_id.in_(select([wholesale.c.product_id])))

        total = await database.execute(query=select([func.count()]).select_from(query.alias()).as_scalar())
        query = query.limit(kwargs['per_page']).offset((kwargs['page'] - 1) * kwargs['per_page'])
        product_db = await database.fetch_all(query=query)

        paginate = Pagination(kwargs['page'], kwargs['per_page'], total, product_db)
        product_data = [{index:value for index,value in item.items()} for item in paginate.items]
        [data.__setitem__('products_wholesale', await ProductLogic.check_wholesale(data['products_id'])) for data in product_data]
        return {
            "data": product_data,
            "total": paginate.total,
            "next_num": paginate.next_num,
            "prev_num": paginate.prev_num,
            "page": paginate.page,
            "iter_pages": [x for x in paginate.iter_pages()]
        }

    @staticmethod
    async def get_product_by_slug(slug: str) -> dict:
        query = select([product]).where(product.c.slug == slug).apply_labels()
        product_db = await database.fetch_one(query=query)
        product_data = {index:value for index,value in product_db.items()}

        # get item sub category with parent
        query = select([item_sub_category.join(sub_category.join(category))]) \
            .where(item_sub_category.c.id == product_data['products_item_sub_category_id']).apply_labels()
        category_db = await database.fetch_one(query=query)
        product_data['products_category'] = {index:value for index,value in category_db.items()}

        # get brand
        query = select([brand]).where(brand.c.id == product_data['products_brand_id']).apply_labels()
        brand_db = await database.fetch_one(query=query)
        product_data['products_brand'] = {index:value for index,value in brand_db.items()} if brand_db else {}

        # get variant
        product_data['products_variant'] = await VariantFetch.get_variant_by_product_id(product_data['products_id'])

        # get wholesale
        query = select([wholesale]).where(wholesale.c.product_id == product_data['products_id']).apply_labels()
        wholesale_db = await database.fetch_all(query=query)
        product_data['products_wholesale'] = [{index:value for index,value in item.items()} for item in wholesale_db]

        return product_data

    @staticmethod
    async def filter_by_slug(slug: str) -> product:
        query = select([product]).where(product.c.slug == slug)
        return await database.fetch_one(query=query)

    @staticmethod
    async def filter_by_id(id_: int) -> product:
        query = select([product]).where(product.c.id == id_)
        return await database.fetch_one(query=query)
