from sqlalchemy import Table, Column, Integer, String
from config import metadata

shipping_province = Table('shipping_provinces', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100), unique=True, index=True, nullable=False)
)
