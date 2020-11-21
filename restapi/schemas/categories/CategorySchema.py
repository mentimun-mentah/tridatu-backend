from pydantic import BaseModel, StrictStr

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
