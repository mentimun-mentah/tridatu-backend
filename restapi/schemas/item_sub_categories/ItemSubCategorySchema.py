from pydantic import BaseModel, constr, conint

class ItemSubCategorySchema(BaseModel):
    sub_category_id: conint(strict=True, gt=0)
    name: constr(strict=True)

    class Config:
        min_anystr_length = 3
        max_anystr_length = 100
        anystr_strip_whitespace = True

class ItemSubCategoryCreateUpdate(ItemSubCategorySchema):
    pass

class ItemSubCategoryData(ItemSubCategorySchema):
    id: int
