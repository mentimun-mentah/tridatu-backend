from pydantic import BaseModel

class OutletSchema(BaseModel):
    id: int
    image: str
