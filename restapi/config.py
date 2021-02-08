from redis import Redis
from sqlalchemy import MetaData
from databases import Database
from datetime import timedelta
from fastapi_jwt_auth import AuthJWT
from fastapi.templating import Jinja2Templates
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
from pydantic import BaseSettings, PostgresDsn, validator
from typing import Optional, Literal

with open("public_key.txt") as f:
    public_key = f.read().strip()

with open("private_key.txt") as f:
    private_key = f.read().strip()

class Settings(BaseSettings):
    authjwt_token_location: set = {"cookies"}
    authjwt_secret_key: str
    authjwt_algorithm: str = "RS512"
    authjwt_public_key: str = public_key
    authjwt_private_key: str = private_key
    authjwt_denylist_enabled: bool = True
    authjwt_cookie_domain: Optional[str] = None
    authjwt_cookie_secure: bool
    authjwt_cookie_samesite: str = "lax"

    rajaongkir_key: str
    frontend_uri: str
    database_uri: PostgresDsn
    redis_db_host: str
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_tls: bool

    timezone: str
    stage_app: Literal['production','development']

    access_expires: Optional[int] = None
    access_expires_admin: Optional[int] = None
    refresh_expires: Optional[int] = None

    GOOGLE_REDIRECT_URI: str
    FACEBOOK_REDIRECT_URI: str

    @validator('database_uri')
    def validate_database_uri(cls, v):
        assert v.path and len(v.path) > 1, 'database must be provided'
        return v

    @validator('access_expires',always=True)
    def parse_access_expires(cls, v):
        return int(timedelta(minutes=15).total_seconds())

    @validator('access_expires_admin',always=True)
    def parse_access_expires_admin(cls, v):
        return int(timedelta(hours=3).total_seconds())

    @validator('refresh_expires',always=True)
    def parse_refresh_expires(cls, v):
        return int(timedelta(days=30).total_seconds())

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


metadata = MetaData()
settings = Settings()
database = Database(settings.database_uri)
templates = Jinja2Templates(directory="templates")
redis_conn = Redis(host=settings.redis_db_host, port=6379, db=0, decode_responses=True)
config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

oauth.register(
    name='facebook',
    api_base_url='https://graph.facebook.com/v7.0/',
    access_token_url='https://graph.facebook.com/v7.0/oauth/access_token',
    authorize_url='https://www.facebook.com/v7.0/dialog/oauth',
    client_kwargs={'scope': 'email public_profile'},
)

@AuthJWT.load_config
def get_config():
    return settings

@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token['jti']
    entry = redis_conn.get(jti)
    return entry and entry == 'true'
