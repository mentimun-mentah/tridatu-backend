from sqlalchemy import Table, Column, Integer, BigInteger, ForeignKey
from config import metadata

wholesale = Table('wholesale', metadata,
    Column('id', BigInteger, primary_key=True),
    Column('min_qty', Integer, nullable=False),
    Column('price', BigInteger, nullable=False),
    Column('product_id', BigInteger,ForeignKey('products.id',onupdate='cascade',ondelete='cascade'),nullable=False),
)
