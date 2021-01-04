from sqlalchemy import Table, Column, Integer, String
from config import metadata

brand = Table('brands', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100), unique=True, index=True, nullable=False),
    Column('image', String(100), nullable=False)
)
