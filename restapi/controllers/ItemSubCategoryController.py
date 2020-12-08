from config import database
from sqlalchemy.sql import select
from models.ItemSubCategoryModel import item_sub_category

class ItemSubCategoryLogic:
    pass

class ItemSubCategoryCrud:
    @staticmethod
    async def create_item_sub_category(**kwargs) -> int:
        return await database.execute(query=item_sub_category.insert(),values=kwargs)

    @staticmethod
    async def update_item_sub_category(id_: int, **kwargs) -> None:
        query = item_sub_category.update().where(item_sub_category.c.id_item_sub_category == id_)
        await database.execute(query=query,values=kwargs)

    @staticmethod
    async def delete_item_sub_category(id_: int) -> None:
        query = item_sub_category.delete().where(item_sub_category.c.id_item_sub_category == id_)
        await database.execute(query=query)

class ItemSubCategoryFetch:
    @staticmethod
    async def get_all_item_sub_categories() -> item_sub_category:
        return await database.fetch_all(query=select([item_sub_category]).order_by(item_sub_category.c.sub_category_id))

    @staticmethod
    async def check_duplicate_name(sub_category_id: int, name: str) -> item_sub_category:
        query = select([item_sub_category]) \
            .where(
                (item_sub_category.c.name_item_sub_category == name) &
                (item_sub_category.c.sub_category_id == sub_category_id))
        return await database.fetch_one(query=query)

    @staticmethod
    async def filter_by_id(id_: int) -> item_sub_category:
        query = select([item_sub_category]).where(item_sub_category.c.id_item_sub_category == id_)
        return await database.fetch_one(query=query)
