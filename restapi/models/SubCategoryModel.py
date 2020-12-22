from sqlalchemy import Table, Column, Integer, String, ForeignKey
from config import metadata

sub_category = Table('sub_categories', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100), nullable=False),
    Column('category_id', Integer,ForeignKey('categories.id',onupdate='cascade',ondelete='cascade'),nullable=False)
)
