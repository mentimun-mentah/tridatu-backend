from pydantic import BaseModel, StrictStr
from typing import Optional, List

class CategorySchema(BaseModel):
    name_category: StrictStr

    class Config:
        min_anystr_length = 3
        max_anystr_length = 100
        anystr_strip_whitespace = True

class CategoryCreateUpdate(CategorySchema):
    pass

class CategoryData(CategorySchema):
    id_category: int
    name_sub_category: Optional[str]
    id_sub_category: Optional[int]

# ========= CATEGORY WITH CHILDREN IN DB =========

class ItemSubCategoryInDb(BaseModel):
    id_item_sub_category: int
    name_item_sub_category: str

class SubCategoryInDb(BaseModel):
    id_sub_category: int
    name_sub_category: str
    item_sub_categories: List[ItemSubCategoryInDb]

class CategoryWithChildrenData(BaseModel):
    id_category: int
    name_category: str
    sub_categories: List[SubCategoryInDb]
