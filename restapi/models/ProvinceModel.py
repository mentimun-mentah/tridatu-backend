from sqlalchemy import Table, Column, Integer, String
from config import metadata

province = Table('provinces', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100), unique=True, index=True, nullable=False),
    Column('code', Integer, unique=True, index=True, nullable=False)
)
