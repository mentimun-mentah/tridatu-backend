from pydantic import BaseModel, constr, conint

class SubCategorySchema(BaseModel):
    category_id: conint(strict=True, gt=0)
    name: constr(strict=True, min_length=3, max_length=100)

    class Config:
        min_anystr_length = 1
        anystr_strip_whitespace = True

class SubCategoryCreateUpdate(SubCategorySchema):
    pass

class SubCategoryData(SubCategorySchema):
    id: int
