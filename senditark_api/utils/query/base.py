import datetime
from typing import (
    Dict,
    List,
    Optional,
    Type,
    Union,
)

from pukr import get_logger
from sqlalchemy.orm import (
    DeclarativeMeta,
    InstrumentedAttribute,
    Session,
)
from sqlalchemy.sql.elements import (
    BinaryExpression,
    UnaryExpression,
)

log = get_logger()

ModelDictType = Dict[
    Union[InstrumentedAttribute, str],
    Union[str, int, List[str], List[int], datetime.date, datetime.datetime]
]
FilterListType = List[Union[BinaryExpression, bool]]


class BaseQueryHelper:
    log = log

    @classmethod
    def _add_obj(cls, session: Session, obj_class: Type[DeclarativeMeta], data: ModelDictType = None,
                 obj: DeclarativeMeta = None):
        if data is not None:
            cleaned_dict = {}
            # Iterate through the dict and determine whether a key needs to be converted to string
            for k, v in data.items():
                if isinstance(k, InstrumentedAttribute):
                    cleaned_dict[k.name] = v
                else:
                    cleaned_dict[k] = v

            obj = obj_class(**cleaned_dict)
        elif obj is None:
            raise ValueError(f'Cannot create and add object of class {obj_class}. '
                             f'Parameters data or obj must not be empty')
        session.add(obj)
        session.commit()
        return obj

    @classmethod
    def _get_obj(cls, session: Session, obj_class: Type[DeclarativeMeta],
                 filters: FilterListType) -> Optional:
        # TODO: add is_deleted to filters if not included?
        return session.query(obj_class).filter(*filters).one_or_none()

    @classmethod
    def _get_objs(cls, session: Session, obj_class: Type[DeclarativeMeta],
                  filters: List[Union[BinaryExpression, bool]] = None,
                  limit: int = None, order_by: Union[InstrumentedAttribute, UnaryExpression] = None) -> List:
        if filters is None:
            filters = []
        # TODO: add is_deleted to filters if not included?

        query = session.query(obj_class).filter(*filters)
        if order_by is not None:
            query = query.order_by(order_by)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    @classmethod
    def _edit_obj(cls, session: Session, obj: DeclarativeMeta, data: ModelDictType):
        for k, v in data.items():
            setattr(obj, k.name, v)
        session.commit()
        return obj

    @classmethod
    def _build_filters(cls, filter_mapping: Dict) -> List:
        """
        Builds filters by taking in a filter mapping to desired value.

        Examples:
            >>> cls._build_filters({
            >>>    TableAccount.account_type: AccountType.ASSET,
            >>>    TableAccount.name: ['CHECKING', 'SAVINGS']
            >>>})

        Args:
            filter_mapping: dict, key is the table attribute, value is the expected value(s)

        Returns:
            List of filters to apply to an ORM query
        """
        filters = []

        for tbl_attr, attr in filter_mapping.items():
            if attr is not None:
                if isinstance(attr, list):
                    filt = tbl_attr.in_(attr)
                else:
                    filt = tbl_attr == attr
                filters.append(filt)
        return filters

    @classmethod
    def get_or_create(cls, session: Session, obj, attrs: Union[str, List[str]]):
        if isinstance(attrs, str):
            attrs = [attrs]
        filters = []
        for attr in attrs:
            filters.append(getattr(obj.__class__, attr) == getattr(obj, attr))

        retrieved_obj = (session.query(obj.__class__).filter(*filters).one_or_none())
        if retrieved_obj is None:
            log.debug(f'Obj ({obj}) did not exist. Adding...')
            session.add(obj)
            session.commit()
            return obj
        else:
            log.debug(f'Obj ({retrieved_obj}) existed. Returning without adding')
        return retrieved_obj
