from sqlalchemy import Table, Column, Integer, String, ForeignKey
from config import metadata

shipping_city = Table('shipping_cities', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100), nullable=False),
    Column('type', String(20), nullable=False),
    Column(
        'shipping_province_id', Integer,
        ForeignKey('shipping_provinces.id',onupdate='cascade',ondelete='cascade'),
        nullable=False
    )
)
