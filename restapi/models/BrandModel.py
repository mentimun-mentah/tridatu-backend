from sqlalchemy import Table, Column, Integer, String
from config import metadata

brand = Table('brands', metadata,
    Column('id_brand', Integer, primary_key=True),
    Column('name_brand', String(100), unique=True, index=True, nullable=False),
    Column('image_brand', String(100), nullable=False)
)
