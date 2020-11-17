from sqlalchemy import Table, Column, Integer, String, Text, BigInteger, DateTime, ForeignKey, Boolean, func
from sqlalchemy.sql import expression
from config import metadata

address = Table('addresses', metadata,
    Column('id', Integer, primary_key=True),
    Column('label', String(100), nullable=False),
    Column('receiver', String(100), nullable=False),
    Column('phone', String(20), nullable=False),
    Column('region', Text, nullable=False),
    Column('postal_code', BigInteger, nullable=False),
    Column('recipient_address', Text, nullable=False),
    Column('main_address', Boolean, server_default=expression.false()),
    Column('created_at', DateTime, default=func.now()),
    Column('updated_at', DateTime, default=func.now()),
    Column('user_id', Integer, ForeignKey('users.id',onupdate='cascade',ondelete='cascade'), nullable=False)
)