from sqlalchemy import Table, Column, Integer, String, ForeignKey
from config import metadata

postal_code = Table('postal_codes', metadata,
    Column('id', Integer, primary_key=True),
    Column('urban', String(100), nullable=False),
    Column('sub_district', String(100), nullable=False),
    Column('city', String(100), nullable=False),
    Column('postal_code', Integer, nullable=False),
    Column('province_code', Integer, ForeignKey('provinces.code',onupdate='cascade',ondelete='cascade'), nullable=False)
)
