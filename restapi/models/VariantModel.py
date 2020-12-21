from sqlalchemy import Table, Column, Integer, String, BigInteger, ForeignKey
from config import metadata

variant = Table('variants', metadata,
    Column('id_variant', BigInteger, primary_key=True),
    Column('name_variant', String(50), nullable=True),
    Column('option_variant', String(50), nullable=True),
    Column('price_variant', BigInteger, nullable=False),
    Column('stock_variant', Integer, nullable=False),
    Column('code_variant', String(100), nullable=True),
    Column('barcode_variant', String(100), nullable=True),
    Column('image_variant', String(100), nullable=True),
    Column(
        'product_id', Integer,
        ForeignKey('products.id_product',onupdate='cascade',ondelete='cascade'),
        nullable=False
    )
)
