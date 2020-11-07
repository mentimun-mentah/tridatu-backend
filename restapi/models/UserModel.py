from sqlalchemy import Table, Column, Integer, String, DateTime, func
from config import metadata

users = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String(100), nullable=False),
    Column('email', String(100), unique=True, index=True, nullable=False),
    Column('password', String(100), nullable=True),
    Column('role', String(10), server_default="guest"),
    Column('avatar', String(100), server_default="default.jpg"),
    Column('created_at', DateTime, default=func.now()),
    Column('updated_at', DateTime, default=func.now()),
)
