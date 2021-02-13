from sqlalchemy import Table, Column, BigInteger, ForeignKey
from config import metadata

wishlist = Table('wishlists', metadata,
    Column('id', BigInteger, primary_key=True),
    Column('product_id', BigInteger,ForeignKey('products.id',onupdate='cascade',ondelete='cascade'),nullable=False),
    Column('user_id', BigInteger, ForeignKey('users.id',onupdate='cascade',ondelete='cascade'), nullable=False)
)
