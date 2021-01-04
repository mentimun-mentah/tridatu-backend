from sqlalchemy import Table, Column, Integer, String, ForeignKey
from config import metadata

item_sub_category = Table('item_sub_categories', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100), nullable=False),
    Column('sub_category_id', Integer,ForeignKey('sub_categories.id',onupdate='cascade',ondelete='cascade'),nullable=False)
)
