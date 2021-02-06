from sqlalchemy import (
    Table, Column, Integer, String,
    Text, Boolean, BigInteger, DateTime,
    ForeignKey, func
)
from sqlalchemy.sql import expression, text
from config import metadata

product = Table('products', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100), unique=True, index=True, nullable=False),
    Column('slug', Text, unique=True, index=True, nullable=False),
    Column('desc', Text, nullable=False),
    Column('condition', Boolean, nullable=False),
    Column('image_product', Text, nullable=False),
    Column('weight', BigInteger, nullable=False),
    Column('image_size_guide', String(100), nullable=True),
    Column('video', String(100), nullable=True),
    Column('preorder', Integer, nullable=True),
    Column('live', Boolean, server_default=expression.false()),
    Column('visitor', BigInteger, server_default=text("0")),
    Column('discount_start', DateTime, nullable=True),
    Column('discount_end', DateTime, nullable=True),

    Column(
        'item_sub_category_id', Integer,
        ForeignKey('item_sub_categories.id',onupdate='cascade',ondelete='cascade'),
        nullable=False
    ),
    Column('brand_id', Integer, ForeignKey('brands.id',onupdate='cascade',ondelete='cascade'), nullable=True),
    Column('created_at', DateTime, default=func.now()),
    Column('updated_at', DateTime, default=func.now()),
)
