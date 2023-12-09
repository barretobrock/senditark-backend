from typing import (
    Dict,
    List,
)

from sqlalchemy.orm import Session
from sqlalchemy.sql import asc

from senditark_api.model import TableAccount
from senditark_api.utils.query.base import (
    BaseQueryHelper,
    FilterListType,
    ModelDictType,
)


class AccountQueries(BaseQueryHelper):

    @classmethod
    def add_account(cls, session: Session, data: ModelDictType):
        return cls._add_obj(session=session, obj_class=TableAccount, data=data)

    @classmethod
    def get_account(cls, session: Session, account_id: int = None, filters: FilterListType = None) -> TableAccount:
        if filters is None:
            filters = [TableAccount.account_id == account_id]
        return cls._get_obj(session=session, obj_class=TableAccount, filters=filters)

    @classmethod
    def get_accounts(cls, session: Session, filters: FilterListType = None, limit: int = None) -> List[TableAccount]:
        return cls._get_objs(session=session, obj_class=TableAccount, filters=filters, limit=limit,
                             order_by=asc(TableAccount.full_name))

    @classmethod
    def edit_account(cls, session: Session, account_id: int, data: ModelDictType):
        account = cls.get_account(session=session, account_id=account_id)
        if account is None:
            raise ValueError(f'Failed to find account with id: {account_id}')
        return cls._edit_obj(session=session, obj=account, data=data)

    @classmethod
    def get_account_data(cls, session: Session, account_id: int, account_obj: TableAccount = None) -> Dict:
        """Transforms TableAccount data into a flattened dictionary for API responses"""
        if account_obj is None:
            account_obj = cls.get_account(session=session, account_id=account_id)

        return {
            'account_id': account_obj.account_id,
            'name': account_obj.name,
            'full_name': account_obj.full_name,
            'parent_account_key': account_obj.parent_account_key,
            'level': account_obj.level,
            'account_type': account_obj.account_type.value,
            'account_currency': account_obj.account_currency.name,
            'is_hidden': account_obj.is_hidden,
        }

    @classmethod
    def delete_account(cls, session: Session, account_id: int):
        cls.log.info(f'Handling DELETE for ACCOUNT ({account_id})')

        account = cls.get_account(session=session, account_id=account_id)
        session.delete(account)
        session.commit()
