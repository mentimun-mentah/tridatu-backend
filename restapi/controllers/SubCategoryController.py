from config import database
from sqlalchemy.sql import select
from models.SubCategoryModel import sub_category

class SubCategoryLogic:
    pass

class SubCategoryCrud:
    async def create_sub_category(**kwargs) -> int:
        return await database.execute(query=sub_category.insert(),values=kwargs)

    async def update_sub_category(id_: int, **kwargs) -> None:
        await database.execute(query=sub_category.update().where(sub_category.c.id_sub_category == id_),values=kwargs)

    async def delete_sub_category(id_: int) -> None:
        await database.execute(query=sub_category.delete().where(sub_category.c.id_sub_category == id_))

class SubCategoryFetch:
    async def get_all_sub_categories() -> sub_category:
        return await database.fetch_all(query=select([sub_category]))

    async def filter_by_name(name: str) -> sub_category:
        query = select([sub_category]).where(sub_category.c.name_sub_category == name)
        return await database.fetch_one(query=query)

    async def filter_by_id(id_: int) -> sub_category:
        query = select([sub_category]).where(sub_category.c.id_sub_category == id_)
        return await database.fetch_one(query=query)
