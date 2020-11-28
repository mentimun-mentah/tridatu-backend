from sqlalchemy import (
    Table, Column, Integer, String,
    Text, Boolean, BigInteger, DateTime,
    ForeignKey, func
)
from config import metadata

product = Table('products', metadata,
    Column('id_product', Integer, primary_key=True),
    Column('name_product', String(100), unique=True, index=True, nullable=False),
    Column('slug_product', Text, unique=True, index=True, nullable=False),
    Column('desc_product', Text, nullable=False),
    Column('condition_product', Boolean, nullable=False),
    Column('image_product', Text, nullable=False),
    Column('weight_product', BigInteger, nullable=False),
    Column('image_size_guide_product', String(100), nullable=True),
    Column('video_product', String(100), nullable=True),
    Column('preorder_product', Integer, nullable=True),

    Column(
        'item_sub_category_id', Integer,
        ForeignKey('item_sub_categories.id_item_sub_category',onupdate='cascade',ondelete='cascade'),
        nullable=False
    ),
    Column('brand_id', Integer, ForeignKey('brands.id_brand',onupdate='cascade',ondelete='cascade'), nullable=True),
    Column('created_at', DateTime, default=func.now()),
    Column('updated_at', DateTime, default=func.now()),
)
