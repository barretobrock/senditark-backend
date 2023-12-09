from typing import (
    Dict,
    List,
)

from sqlalchemy.orm import Session

from senditark_api.model import TableBalance
from senditark_api.utils.query.base import (
    BaseQueryHelper,
    FilterListType,
    ModelDictType,
)


class BalanceQueries(BaseQueryHelper):

    @classmethod
    def add_balance(cls, session: Session, data: ModelDictType) -> TableBalance:
        return cls._add_obj(session=session, obj_class=TableBalance, data=data)

    @classmethod
    def get_balance(cls, session: Session, balance_id: int = None, filters: FilterListType = None) -> TableBalance:
        if filters is None:
            filters = [TableBalance.balance_id == balance_id]
        return cls._get_obj(session=session, obj_class=TableBalance, filters=filters)

    @classmethod
    def get_balances(cls, session: Session, filters: FilterListType = None, limit: int = 100) -> List[TableBalance]:
        return cls._get_objs(session=session, obj_class=TableBalance, filters=filters, limit=limit)

    @classmethod
    def edit_balance(cls, session: Session, balance_id: int, data: ModelDictType):
        balance_obj = cls.get_balance(session=session, balance_id=balance_id)
        if balance_obj is None:
            raise ValueError(f'Failed to find balance with id: {balance_id}')

        cls._edit_obj(session=session, obj=balance_obj, data=data)

    @classmethod
    def get_balance_data(cls, session: Session, balance_id: int = None, balance_obj: TableBalance = None) -> Dict:
        if balance_obj is None:
            balance_obj = cls.get_balance(session=session, balance_id=balance_id)

        return {
            'balance_id': balance_obj.balance_id,
            'account_key': balance_obj.account_key,
            'date': balance_obj.date,
            'amount': balance_obj.amount
        }

    @classmethod
    def delete_balance(cls, session: Session, balance_id: int):
        cls.log.info(f'Handling DELETE for BALANCE ({balance_id})')

        balance = cls.get_balance(session=session, balance_id=balance_id)

        session.delete(balance)
        session.commit()
