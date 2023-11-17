import os
import pathlib
import random
import string
from typing import Dict

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from senditark_api import (
    __update_date__,
    __version__,
)
from senditark_api.model.base import Base

ROOT = pathlib.Path(__file__).parent.parent
HOME = pathlib.Path().home()
KEY_DIR = HOME.joinpath('keys')
LOG_DIR = HOME.joinpath('logs')
DATA_DIR = HOME.joinpath('data').joinpath('senditark_backups')


def read_secrets(path_obj: pathlib.Path) -> Dict:
    secrets = {}
    with path_obj.open('r') as f:
        for item in f.readlines():
            k, v = item.split('=', 1)
            secrets[k] = v.strip()
    return secrets


class BaseConfig:
    """
    See https://flask.palletsprojects.com/en/2.2.x/config/ for help!

    """
    ENV = 'development'
    NAME = 'senditark'
    VERSION = __version__
    UPDATE_DATE = __update_date__
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        SECRET_KEY = ''.join(random.choice(string.ascii_lowercase) for i in range(32))

    SECRETS = None
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{db-username}:{db-password}@{db-host}:{db-port}/{db-database}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION = None

    @classmethod
    def load_secrets(cls):
        secrets_path = ROOT.joinpath('secretprops.properties')
        if cls.ENV == 'production':
            secrets_path = KEY_DIR.joinpath('senditark.properties')
        return read_secrets(secrets_path)

    @classmethod
    def build_db_engine(cls):
        """Builds database engine, sets SESSION"""
        if cls.SECRETS is None:
            cls.SECRETS = cls.load_secrets()
        cls.SQLALCHEMY_DATABASE_URI = cls.SQLALCHEMY_DATABASE_URI.format(**cls.SECRETS)
        engine = create_engine(cls.SQLALCHEMY_DATABASE_URI, isolation_level='SERIALIZABLE')
        Base.metadata.bind = engine
        cls.SESSION = sessionmaker(bind=engine)


class DevelopmentConfig(BaseConfig):
    ENV = 'development'
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    DB_SERVER = 'localhost'
    PORT = 5000


class ProductionConfig(BaseConfig):
    ENV = 'production'
    DEBUG = False
    LOG_LEVEL = 'DEBUG'
    DB_SERVER = '0.0.0.0'
    PORT = 5007
