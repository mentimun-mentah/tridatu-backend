from config import database
from sqlalchemy.sql import select
from models.CategoryModel import category
from models.SubCategoryModel import sub_category
from models.ItemSubCategoryModel import item_sub_category

class CategoryLogic:
    pass

class CategoryCrud:
    async def create_category(name: str) -> int:
        return await database.execute(query=category.insert(),values={'name_category': name})

    async def update_category(id_: int, **kwargs) -> None:
        await database.execute(query=category.update().where(category.c.id_category == id_),values=kwargs)

    async def delete_category(id_: int) -> None:
        await database.execute(query=category.delete().where(category.c.id_category == id_))

class CategoryFetch:
    async def get_all_categories(with_sub: bool) -> category:
        if with_sub is False:
            return await database.fetch_all(query=select([category]))
        return await database.fetch_all(select([sub_category.join(category)]))

    async def get_categories_with_children() -> list:
        category_db = await database.fetch_all(query=select([category]))
        category_data = [{index:value for index,value in x.items()} for x in category_db]

        for item in category_data:
            query = select([sub_category]).where(sub_category.c.category_id == item['id_category'])
            sub_category_db = await database.fetch_all(query=query)
            item['sub_categories'] = [{index:value for index,value in x.items()} for x in sub_category_db]

            for item_two in item['sub_categories']:
                query = select([item_sub_category]) \
                    .where(item_sub_category.c.sub_category_id == item_two['id_sub_category'])
                item_sub_category_db = await database.fetch_all(query=query)
                item_two['item_sub_categories'] = [
                    {index:value for index,value in x.items()} for x in item_sub_category_db
                ]

        return category_data

    async def filter_by_name(name: str) -> category:
        query = select([category]).where(category.c.name_category == name)
        return await database.fetch_one(query=query)

    async def filter_by_id(id_: int) -> category:
        query = select([category]).where(category.c.id_category == id_)
        return await database.fetch_one(query=query)
