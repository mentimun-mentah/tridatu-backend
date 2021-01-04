from pydantic import BaseModel, constr, conint

class SubCategorySchema(BaseModel):
    category_id: conint(strict=True, gt=0)
    name: constr(strict=True)

    class Config:
        min_anystr_length = 3
        max_anystr_length = 100
        anystr_strip_whitespace = True

class SubCategoryCreateUpdate(SubCategorySchema):
    pass

class SubCategoryData(SubCategorySchema):
    id: int
