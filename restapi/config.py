from fastapi_jwt_auth import AuthJWT
from fastapi.templating import Jinja2Templates
from sqlalchemy import MetaData
from databases import Database
from redis import Redis
from pydantic import (
    BaseSettings,
    PostgresDsn,
    RedisDsn,
    validator
)

with open("public_key.txt") as f:
    public_key = f.read().strip()

with open("private_key.txt") as f:
    private_key = f.read().strip()

class Settings(BaseSettings):
    authjwt_token_location: set = {"headers","cookies"}
    authjwt_secret_key: str = "secret"  # change in production
    authjwt_algorithm: str = "RS512"
    authjwt_public_key: str = public_key
    authjwt_private_key: str = private_key
    authjwt_denylist_enabled: bool = True
    authjwt_cookie_secure: bool = False  # change in production
    authjwt_cookie_samesite: str = "lax"

    frontend_uri: str
    database_uri: PostgresDsn
    redis_uri: RedisDsn
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_tls: bool

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
templates = Jinja2Templates(directory="templates")
redis_conn = Redis(host='localhost', port=6379, db=0, decode_responses=True)

@AuthJWT.load_config
def get_config():
    return settings

@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token['jti']
    entry = redis_conn.get(jti)
    return entry and entry == 'true'
