from config import database
from sqlalchemy.sql import select
from models.CategoryModel import category
from models.SubCategoryModel import sub_category
from models.ItemSubCategoryModel import item_sub_category
from typing import Optional

class CategoryLogic:
    @staticmethod
    def extract_categories_with_children(data: list) -> list:
        duplicate_id = list(set([item['categories_id'] for item in data]))

        result = list()
        for id_ in duplicate_id:
            tmp = dict()
            for item in data:
                # initial var
                categories_id = item['categories_id']
                categories_name = item['categories_name']
                sub_categories_id = item['sub_categories_id']
                sub_categories_name = item['sub_categories_name']
                sub_categories_category_id = item['sub_categories_category_id']
                item_sub_categories_id = item['item_sub_categories_id']
                item_sub_categories_name = item['item_sub_categories_name']
                item_sub_categories_sub_category_id = item['item_sub_categories_sub_category_id']

                if id_ == categories_id:
                    # append categories
                    if len(tmp) == 0:
                        tmp.update({
                            'categories_id': categories_id,
                            'categories_name': categories_name,
                            'sub_categories': []
                        })
                    # append sub categories if exists
                    if (
                        sub_categories_id is not None and
                        sub_categories_id not in [check['sub_categories_id'] for check in tmp['sub_categories']]
                    ):
                        tmp['sub_categories'].append({
                            'sub_categories_id': sub_categories_id,
                            'sub_categories_name': sub_categories_name,
                            'sub_categories_category_id': sub_categories_category_id,
                            'item_sub_categories': []
                        })
                    # append item sub categories if exists
                    if (
                        item_sub_categories_sub_category_id is not None and
                        item_sub_categories_sub_category_id in [
                            check['sub_categories_id'] for check in tmp['sub_categories']
                        ]
                    ):
                        idx = [
                            index for index,value in enumerate(tmp['sub_categories'])
                            if value['sub_categories_id'] == item_sub_categories_sub_category_id
                        ][0]

                        tmp['sub_categories'][idx]['item_sub_categories'].append({
                            'item_sub_categories_id': item_sub_categories_id,
                            'item_sub_categories_name': item_sub_categories_name,
                            'item_sub_categories_sub_category_id': item_sub_categories_sub_category_id
                        })

            result.append(tmp)

        return result

class CategoryCrud:
    @staticmethod
    async def create_category(name: str) -> int:
        return await database.execute(query=category.insert(),values={'name': name})

    @staticmethod
    async def update_category(id_: int, **kwargs) -> None:
        await database.execute(query=category.update().where(category.c.id == id_),values=kwargs)

    @staticmethod
    async def delete_category(id_: int) -> None:
        await database.execute(query=category.delete().where(category.c.id == id_))

class CategoryFetch:
    @staticmethod
    async def get_all_categories(with_sub: bool, q: Optional[str]) -> category:
        if with_sub is False:
            query = select([category]).apply_labels()
            if q:
                query = query.where(category.c.name.ilike(f"%{q}%"))
        else:
            query = select([sub_category.join(category)]).apply_labels()
            if q:
                query = query.where((category.c.name.ilike(f"%{q}%")) | (sub_category.c.name.ilike(f"%{q}%")))

        return await database.fetch_all(query=query)

    @staticmethod
    async def get_categories_with_children(q: Optional[str]) -> list:
        category_alias = select([category.outerjoin(sub_category.outerjoin(item_sub_category))]) \
            .apply_labels().alias()

        query = select([category_alias])

        if q:
            query = query.where(
                (category_alias.c.categories_name.ilike(f"%{q}%")) |
                (category_alias.c.sub_categories_name.ilike(f"%{q}%")) |
                (category_alias.c.item_sub_categories_name.ilike(f"%{q}%"))
            )

        category_db = await database.fetch_all(query=query)
        category_data = [{index:value for index,value in x.items()} for x in category_db]
        return CategoryLogic.extract_categories_with_children(category_data)

    @staticmethod
    async def filter_by_name(name: str) -> category:
        query = select([category]).where(category.c.name == name)
        return await database.fetch_one(query=query)

    @staticmethod
    async def filter_by_id(id_: int) -> category:
        query = select([category]).where(category.c.id == id_)
        return await database.fetch_one(query=query)
