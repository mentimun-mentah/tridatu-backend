from config import database
from sqlalchemy.sql import select
from models.CategoryModel import category

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
    async def get_all_categories() -> category:
        return await database.fetch_all(query=select([category]))

    async def filter_by_name(name: str) -> category:
        query = select([category]).where(category.c.name_category == name)
        return await database.fetch_one(query=query)

    async def filter_by_id(id_: int) -> category:
        query = select([category]).where(category.c.id_category == id_)
        return await database.fetch_one(query=query)
