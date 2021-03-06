from sqlalchemy import Table, Column, BigInteger, String, Text, Boolean, DateTime
from config import metadata

promo = Table('promos', metadata,
    Column('id', BigInteger, primary_key=True),
    Column('name', String(100), unique=True, index=True, nullable=False),
    Column('slug', Text, unique=True, index=True, nullable=False),
    Column('desc', Text, nullable=True),
    Column('terms_condition', Text, nullable=True),
    Column('image', String(100), nullable=True),
    Column('seen', Boolean, nullable=False),
    Column('period_start', DateTime, nullable=False),
    Column('period_end', DateTime, nullable=False),
)
