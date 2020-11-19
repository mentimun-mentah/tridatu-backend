from sqlalchemy import Table, Column, Integer, String
from config import metadata

outlet = Table('outlets', metadata,
    Column('id', Integer, primary_key=True),
    Column('image', String(100), nullable=False)
)
