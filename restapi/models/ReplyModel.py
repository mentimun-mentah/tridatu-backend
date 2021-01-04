from sqlalchemy import Table, Column, BigInteger, Text, ForeignKey, DateTime, func
from config import metadata

reply = Table('replies', metadata,
    Column('id', BigInteger, primary_key=True),
    Column('message', Text, nullable=False),
    Column('comment_id', BigInteger, ForeignKey('comments.id',onupdate='cascade',ondelete='cascade'), nullable=False),
    Column('user_id', BigInteger, ForeignKey('users.id',onupdate='cascade',ondelete='cascade'), nullable=False),
    Column('created_at', DateTime, default=func.now())
)
