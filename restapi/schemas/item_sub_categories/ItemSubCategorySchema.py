from pydantic import BaseModel, constr, conint

class ItemSubCategorySchema(BaseModel):
    sub_category_id: conint(strict=True, gt=0)
    name: constr(strict=True, min_length=3, max_length=100)

    class Config:
        min_anystr_length = 1
        anystr_strip_whitespace = True

class ItemSubCategoryCreateUpdate(ItemSubCategorySchema):
    pass

class ItemSubCategoryData(ItemSubCategorySchema):
    id: int
