from sqlalchemy import Table, Column, String, Integer, BigInteger, Boolean, ForeignKey
from sqlalchemy.sql import expression
from config import metadata

confirmation = Table('confirmation_users', metadata,
    Column('id', String(100), primary_key=True),
    Column('activated', Boolean, server_default=expression.false()),
    Column('resend_expired', Integer, nullable=True),
    Column('user_id', BigInteger, ForeignKey('users.id',onupdate='cascade',ondelete='cascade'), nullable=False)
)
