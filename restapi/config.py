from sqlalchemy import MetaData
from databases import Database
from pydantic import BaseSettings, PostgresDsn, validator

class Settings(BaseSettings):
    database_uri: PostgresDsn

    @validator('database_uri')
    def validator_database_ur(cls, v):
        assert v.path and len(v.path) > 1, 'database must be provided'
        return v

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


metadata = MetaData()
settings = Settings()
database = Database(settings.database_uri)
