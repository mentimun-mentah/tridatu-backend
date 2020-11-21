from sqlalchemy import Table, Column, Integer, String
from config import metadata

category = Table('categories', metadata,
    Column('id_category', Integer, primary_key=True),
    Column('name_category', String(100), unique=True, index=True, nullable=False)
)
