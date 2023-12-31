import enum
import re

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    func,
)
from sqlalchemy.ext.declarative import (
    declarative_base,
    declared_attr,
)


class Currency(enum.IntEnum):
    EUR = enum.auto()
    USD = enum.auto()


class Base:
    @classmethod
    @declared_attr
    def __tablename__(cls):
        """Takes in a class name, sets the table name according to the class name, with some manipulation"""
        return '_'.join([x.lower() for x in re.findall(r'[A-Z][^A-Z]*', cls.__name__) if x != 'Table'])

    @classmethod
    @declared_attr
    def __table_args__(cls):
        return {'schema': 'default'}

    @declared_attr
    def created_date(self):
        return Column(TIMESTAMP, server_default=func.now())

    @declared_attr
    def update_date(self):
        return Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    @declared_attr
    def is_deleted(self):
        return Column(Boolean, default=False)


Base = declarative_base(cls=Base)
