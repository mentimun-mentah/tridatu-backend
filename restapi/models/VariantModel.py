from sqlalchemy import Table, Column, Integer, String, BigInteger, ForeignKey
from config import metadata

variant = Table('variants', metadata,
    Column('id', BigInteger, primary_key=True),
    Column('name', String(50), nullable=True),
    Column('option', String(50), nullable=True),
    Column('price', BigInteger, nullable=False),
    Column('stock', Integer, nullable=False),
    Column('code', String(100), nullable=True),
    Column('barcode', String(100), nullable=True),
    Column('image', String(100), nullable=True),
    Column('product_id',Integer,ForeignKey('products.id',onupdate='cascade',ondelete='cascade'),nullable=False)
)
