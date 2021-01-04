from sqlalchemy import Table, Column, Integer, String, ForeignKey
from config import metadata

shipping_subdistrict = Table('shipping_subdistricts', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100), nullable=False),
    Column(
        'shipping_city_id', Integer,
        ForeignKey('shipping_cities.id',onupdate='cascade',ondelete='cascade'),
        nullable=False
    )
)
