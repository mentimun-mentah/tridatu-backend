from pydantic import BaseModel, constr, conint

class ItemSubCategorySchema(BaseModel):
    name_item_sub_category: constr(strict=True)
    sub_category_id: conint(strict=True, gt=0)

    class Config:
        min_anystr_length = 3
        max_anystr_length = 100
        anystr_strip_whitespace = True

class ItemSubCategoryCreateUpdate(ItemSubCategorySchema):
    pass

class ItemSubCategoryData(ItemSubCategorySchema):
    id_item_sub_category: int
