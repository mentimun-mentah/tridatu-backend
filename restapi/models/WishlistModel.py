from sqlalchemy import Table, Column, Integer, BigInteger, ForeignKey
from config import metadata

wishlist = Table('wishlists', metadata,
    Column('id_wishlist', BigInteger, primary_key=True),
    Column(
        'product_id', Integer,
        ForeignKey('products.id_product',onupdate='cascade',ondelete='cascade'),
        nullable=False
    ),
    Column('user_id', BigInteger, ForeignKey('users.id',onupdate='cascade',ondelete='cascade'), nullable=False)
)
