from pydantic import BaseModel

class BrandSchema(BaseModel):
    id_brand: int
    name_brand: str
    image_brand: str
