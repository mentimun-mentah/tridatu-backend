from config import database
from sqlalchemy.sql import select
from models.SubCategoryModel import sub_category

class SubCategoryLogic:
    pass

class SubCategoryCrud:
    async def create_sub_category(**kwargs) -> int:
        return await database.execute(query=sub_category.insert(),values=kwargs)

class SubCategoryFetch:
    async def filter_by_name(name: str) -> sub_category:
        query = select([sub_category]).where(sub_category.c.name_sub_category == name)
        return await database.fetch_one(query=query)
