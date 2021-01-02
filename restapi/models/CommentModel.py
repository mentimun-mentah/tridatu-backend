from sqlalchemy import Table, Column, BigInteger, Text, String, ForeignKey, DateTime, func
from config import metadata

comment = Table('comments', metadata,
    Column('id', BigInteger, primary_key=True),
    Column('subject', Text, nullable=False),
    Column('comment_id', BigInteger, nullable=False),
    Column('comment_type', String(20), nullable=False),
    Column('user_id', BigInteger, ForeignKey('users.id',onupdate='cascade',ondelete='cascade'), nullable=False),
    Column('created_at', DateTime, default=func.now())
)
