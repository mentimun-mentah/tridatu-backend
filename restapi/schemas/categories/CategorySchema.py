from pydantic import BaseModel, constr
from typing import Optional, List

class CategorySchema(BaseModel):
    class Config:
        min_anystr_length = 1
        anystr_strip_whitespace = True

class CategoryCreateUpdate(CategorySchema):
    name: constr(strict=True, min_length=3, max_length=100)

class CategoryDataWithoutLabels(CategorySchema):
    id: int
    name: str

class CategoryData(CategorySchema):
    categories_id: int
    categories_name: str
    sub_categories_id: Optional[int]
    sub_categories_name: Optional[str]

# ========= CATEGORY WITH CHILDREN IN DB =========

class ItemSubCategoryInDb(CategorySchema):
    item_sub_categories_id: int
    item_sub_categories_name: str

class SubCategoryInDb(CategorySchema):
    sub_categories_id: int
    sub_categories_name: str
    item_sub_categories: List[ItemSubCategoryInDb]

class CategoryWithChildrenData(CategorySchema):
    categories_id: int
    categories_name: str
    sub_categories: List[SubCategoryInDb]
