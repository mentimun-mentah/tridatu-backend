from pydantic import BaseModel, constr, conint

class SubCategorySchema(BaseModel):
    name_sub_category: constr(strict=True)
    category_id: conint(strict=True, gt=0)

    class Config:
        min_anystr_length = 3
        max_anystr_length = 100
        anystr_strip_whitespace = True

class SubCategoryCreateUpdate(SubCategorySchema):
    pass

class SubCategoryData(SubCategorySchema):
    id_sub_category: int
