import dataclasses
import datetime
from typing import (
    Dict,
    List,
)

from sqlalchemy.orm import Session
from sqlalchemy.sql import (
    and_,
    asc,
    func,
)

from senditark_api.model import (
    TableAccount,
    TableBalance,
)
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
    def get_accounts_with_balance(cls, session: Session) -> List[Dict]:
        # Subquery to grab the latest balance dates for each account
        latest_balance_subq = session.query(TableBalance.account_key, func.max(TableBalance.date).label('date')).\
            filter(TableBalance.date <= datetime.date.today()).\
            group_by(TableBalance.account_key).subquery()
        # Combine with balance table to get actual amounts
        latest_balances = session.query(TableBalance).join(latest_balance_subq, and_(
            latest_balance_subq.c.account_key == TableBalance.account_key,
            latest_balance_subq.c.date == TableBalance.date
        )).subquery()
        # Combine with accounts
        accounts_with_balance = session.query(TableAccount, latest_balances).join(
            latest_balances, TableAccount.account_id == latest_balances.c.account_key).all()

        # We're dealing with an abomination; a combination of whole table along with pieces of another
        #   trailing off at the end. Because of this, we probably shouldn't rely on flask to jsonify this well.
        resp = []
        for (acct_obj, bal_id, _, bal_date, bal, _, _, _) in accounts_with_balance:
            resp_dict = dataclasses.asdict(acct_obj)
            resp_dict.update({
                'balance_id': bal_id,
                'balance': bal,
                'balance_date': bal_date
            })
            resp.append(resp_dict)

        return resp

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


if __name__ == '__main__':
    from senditark_api.config import DevelopmentConfig

    DevelopmentConfig.build_db_engine()
    session = DevelopmentConfig.SESSION()
    aq = AccountQueries
    aq.get_accounts_with_balance(session=session)
