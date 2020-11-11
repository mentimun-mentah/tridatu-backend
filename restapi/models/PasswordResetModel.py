from sqlalchemy import Table, Column, String, Integer, DateTime, func
from config import metadata

password_reset = Table('password_resets', metadata,
    Column('id', String(100), primary_key=True),
    Column('email', String(100), unique=True, index=True, nullable=False),
    Column('resend_expired', Integer, nullable=True),
    Column('created_at', DateTime, default=func.now()),
)
