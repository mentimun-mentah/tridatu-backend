from pydantic import BaseModel

class BrandSchema(BaseModel):
    id: int
    name: str
    image: str
