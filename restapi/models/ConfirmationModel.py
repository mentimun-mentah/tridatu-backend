from sqlalchemy import Table, Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.sql import expression
from config import metadata

confirmation = Table("confirmation", metadata,
    Column('id', String(100), primary_key=True),
    Column('activated', Boolean, server_default=expression.false()),
    Column('resend_expired', Integer, nullable=True),
    Column('user_id', Integer, ForeignKey('users.id',onupdate='cascade',ondelete='cascade'), nullable=False)
)
