from sqlalchemy import Table, Column, Integer, String, Boolean, BigInteger, ForeignKey
from sqlalchemy.sql import expression, text
from config import metadata

variant = Table('variants', metadata,
    Column('id', BigInteger, primary_key=True),
    Column('name', String(50), nullable=True),
    Column('option', String(50), nullable=True),
    Column('price', BigInteger, nullable=False),
    Column('stock', BigInteger, nullable=False),
    Column('code', String(100), nullable=True),
    Column('barcode', String(100), nullable=True),
    Column('image', String(100), nullable=True),
    Column('discount', Integer, server_default=text("0")),
    Column('discount_active', Boolean, server_default=expression.false()),
    Column('product_id',BigInteger,ForeignKey('products.id',onupdate='cascade',ondelete='cascade'),nullable=False)
)
