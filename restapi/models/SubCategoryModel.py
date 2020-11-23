from sqlalchemy import Table, Column, Integer, String, ForeignKey
from config import metadata

sub_category = Table('sub_categories', metadata,
    Column('id_sub_category', Integer, primary_key=True),
    Column('name_sub_category', String(100), nullable=False),
    Column(
        'category_id', Integer,
        ForeignKey('categories.id_category',onupdate='cascade',ondelete='cascade'),
        nullable=False
    )
)
