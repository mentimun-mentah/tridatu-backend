from config import database
from sqlalchemy.sql import select
from models.SubCategoryModel import sub_category

class SubCategoryLogic:
    pass

class SubCategoryCrud:
    @staticmethod
    async def create_sub_category(**kwargs) -> int:
        return await database.execute(query=sub_category.insert(),values=kwargs)

    @staticmethod
    async def update_sub_category(id_: int, **kwargs) -> None:
        await database.execute(query=sub_category.update().where(sub_category.c.id == id_),values=kwargs)

    @staticmethod
    async def delete_sub_category(id_: int) -> None:
        await database.execute(query=sub_category.delete().where(sub_category.c.id == id_))

class SubCategoryFetch:
    @staticmethod
    async def check_duplicate_name(category_id: int, name: str) -> sub_category:
        query = select([sub_category]) \
            .where((sub_category.c.name == name) & (sub_category.c.category_id == category_id))
        return await database.fetch_one(query=query)

    @staticmethod
    async def filter_by_id(id_: int) -> sub_category:
        query = select([sub_category]).where(sub_category.c.id == id_)
        return await database.fetch_one(query=query)
