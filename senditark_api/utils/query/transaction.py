import datetime
from typing import (
    Dict,
    List,
    Union,
)

from sqlalchemy.orm import Session
from sqlalchemy.sql import (
    and_,
    func,
    or_,
)

from senditark_api.model import (
    TableAccount,
    TableBalance,
    TableTransaction,
    TableTransactionSplit,
)
from senditark_api.utils.query.base import (
    BaseQueryHelper,
    FilterListType,
    ModelDictType,
)


class TransactionQueries(BaseQueryHelper):

    @classmethod
    def add_transaction(cls, session: Session, obj: TableTransaction) -> TableTransaction:
        return cls._add_obj(session=session, obj_class=TableTransaction, obj=obj)

    @classmethod
    def get_transaction(cls, session: Session, transaction_id: int = None,
                        filters: FilterListType = None) -> TableTransaction:
        if filters is None:
            filters = [TableTransaction.transaction_id == transaction_id]
        return cls._get_obj(session=session, obj_class=TableTransaction, filters=filters)

    @classmethod
    def get_transactions(cls, session: Session, filters: FilterListType = None, limit: int = 100) -> List[TableTransaction]:
        return cls._get_objs(session=session, obj_class=TableTransaction, filters=filters, limit=limit)

    @classmethod
    def _get_transaction_splits_by_type(
            cls,
            session: Session,
            acct: TableAccount,
            trans_type: str,
            trans_date: datetime.date = None,
            as_sum: bool = False
    ) -> Union[List[TableTransactionSplit], float]:
        """Gets transaction splits by whether they are to credit or debit the account in question"""
        if trans_type not in ['credit', 'debit']:
            raise ValueError(f'Variable trans_type must be one of "credit" or "debit". Was {trans_type}.')

        filters = [TableAccount.account_id == acct.account_id]
        if trans_date is not None:
            filters.append(
                TableTransaction.transaction_date == trans_date
            )
        if trans_type == 'credit':
            # credit
            sum_multiply = -1
            account_join_filter = TableAccount.account_id == TableTransactionSplit.credit_account_key
        else:
            # debit
            sum_multiply = 1
            account_join_filter = TableAccount.account_id == TableTransactionSplit.debit_account_key

        if as_sum:
            results = session.query(func.sum(TableTransactionSplit.amount) * sum_multiply)
        else:
            results = session.query(TableTransactionSplit)
        results = results.join(TableAccount, account_join_filter).\
            join(TableTransaction, TableTransaction.transaction_id == TableTransactionSplit.transaction_key).\
            filter(and_(*filters))
        if as_sum:
            val = results.scalar()
            if val is None:
                return 0
            else:
                return val
        return results.all()

    @classmethod
    def get_all_transaction_splits(cls, session: Session, acct: TableAccount, trans_date: datetime.date = None,
                                   as_sum: bool = True) -> Union[List[TableTransactionSplit], float]:
        credit_splits = cls._get_transaction_splits_by_type(session=session, acct=acct, trans_type='credit',
                                                            trans_date=trans_date, as_sum=as_sum)
        debit_splits = cls._get_transaction_splits_by_type(session=session, acct=acct, trans_type='debit',
                                                           trans_date=trans_date, as_sum=as_sum)
        return credit_splits + debit_splits

    @staticmethod
    def get_transaction_type(credit_account: TableAccount, debit_account: TableAccount) -> str:
        # Generate a string representing the account type of the credit and debit accounts to match with a mapping
        cred_deb_str = f'{credit_account.account_type.name}:{debit_account.account_type.name}'

        cred_deb_mapping = {
            'ASSET:ASSET': 'transfer',
            'ASSET:EXPENSE': 'withdrawal',
            'ASSET:EQUITY': 'invest',
            'ASSET:LIABILITY': 'payoff',
            'EXPENSE:ASSET': 'refund',
            'INCOME:ASSET': 'deposit',
        }
        return cred_deb_mapping.get(cred_deb_str, 'other')

    @classmethod
    def _format_transaction_data(cls, transaction: TableTransaction, account_id: int = None) -> List[Dict]:
        if account_id is not None:
            total = sum([ts.amount * 1 if ts.debit_account_key == account_id else
                         ts.amount * -1 for ts in transaction.splits])
        else:
            total = sum(ts.amount for ts in transaction.splits)

        formatted_transaction = []
        if len(transaction.splits) > 1:
            # Many splits - show only total on top line
            # Populate parent split first
            formatted_transaction.append({
                'sort_key': f'{transaction.transaction_date:%F}-{transaction.transaction_id}-'
                            f'{sum(ts.transaction_split_id for ts in transaction.splits)}',
                'transaction_date': transaction.transaction_date,
                'transaction_id': transaction.transaction_id,
                'is_split_parent': True,
                'is_scheduled': transaction.is_scheduled,
                'desc': transaction.desc,
                'total': total,
            })
            for split in transaction.splits:
                formatted_transaction.append({
                    'sort_key': f'{transaction.transaction_date:%F}-{transaction.transaction_id}-'
                                f'{split.transaction_split_id}',
                    'is_split_parent': False,
                    'amount': split.amount if split.debit_account_key == account_id else split.amount * -1,
                    'payee': split.payee.payee_name,
                    'payee_id': split.payee.payee_id,
                    'credit_account_name': split.credit_account.name,
                    'credit_account_key': split.credit_account_key,
                    'credit_account_type': split.credit_account.account_type.name,
                    'debit_account_name': split.debit_account.name,
                    'debit_account_key': split.debit_account_key,
                    'debit_account_type': split.debit_account.account_type.name,
                    'transaction_type': cls.get_transaction_type(
                        credit_account=split.credit_account, debit_account=split.debit_account),
                    'reconciled_state': split.reconciled_state.value,
                    'invoice_id': '' if split.invoice_split is None else split.invoice_split[0].invoice_key,
                    'invoice_split_id': split.invoice_split_key,
                    'split_memo': split.memo,
                    'tags': [{'name': x.tag.tag_name, 'color': x.tag.tag_color} for x in split.tags]
                })
        else:
            # Just one split - put it all on one line
            split = transaction.splits[0]
            formatted_transaction.append({
                'sort_key': f'{transaction.transaction_date:%F}-{transaction.transaction_id}-'
                            f'{split.transaction_split_id}',
                'transaction_date': transaction.transaction_date,
                'transaction_id': transaction.transaction_id,
                'is_split_parent': True,
                'is_scheduled': transaction.is_scheduled,
                'desc': transaction.desc,
                'total': total,
                'amount': total,
                'payee': split.payee.payee_name,
                'payee_id': split.payee.payee_id,
                'credit_account_name': split.credit_account.name,
                'credit_account_key': split.credit_account_key,
                'credit_account_type': split.credit_account.account_type.name,
                'debit_account_name': split.debit_account.name,
                'debit_account_key': split.debit_account_key,
                'debit_account_type': split.debit_account.account_type.name,
                'transaction_type': cls.get_transaction_type(
                    credit_account=split.credit_account, debit_account=split.debit_account),
                'reconciled_state': split.reconciled_state.name,
                'invoice_id': '' if split.invoice_split is None else split.invoice_split[0].invoice_key,
                'invoice_split_id': split.invoice_split_key,
                'split_memo': split.memo,
                'tags': [{'name': x.tag.tag_name, 'color': x.tag.tag_color} for x in split.tags]
            })
        return formatted_transaction

    @classmethod
    def get_transaction_data(cls, session: Session, transaction_id: int = None,
                             transaction_obj: TableTransaction = None) -> List[Dict]:
        if transaction_obj is None:
            transaction_obj = cls.get_transaction(session=session, transaction_id=transaction_id)

        return cls._format_transaction_data(transaction=transaction_obj)

    @classmethod
    def edit_transaction(cls, session: Session, transaction_id: int, data: ModelDictType):
        transaction = cls.get_transaction(session=session, transaction_id=transaction_id)
        if transaction is None:
            raise ValueError(f'Failed to find transaction with id: {transaction_id}')
        cls._edit_obj(session=session, obj=transaction, data=data)

    @classmethod
    def delete_transaction(cls, session: Session, transaction_id: int):
        cls.log.info(f'Handling DELETE for TRANSACTION ({transaction_id})')
        transaction = cls.get_transaction(session=session, transaction_id=transaction_id)
        # Delete splits as well
        if transaction.splits:
            for split in transaction.splits:
                session.delete(split)
        session.delete(transaction)
        session.commit()

    @classmethod
    def get_transaction_data_by_account(cls, session: Session, account_id: int) -> List[Dict]:
        transactions = session.query(TableTransaction).\
            join(TableTransactionSplit, TableTransactionSplit.transaction_key == TableTransaction.transaction_id).\
            join(TableAccount, or_(
                TableAccount.account_id == TableTransactionSplit.debit_account_key,
                TableAccount.account_id == TableTransactionSplit.credit_account_key
            )).\
            filter(TableAccount.account_id == account_id).all()
        # Format transactions for tabular display
        formatted_transactions = []

        t: TableTransaction
        for t in transactions:
            formatted_transactions += cls._format_transaction_data(transaction=t, account_id=account_id)

        # Sort from most recent, ensuring parent entries (if separate) show up first
        formatted_transactions = sorted(formatted_transactions, key=lambda item: item['sort_key'], reverse=True)

        # Get balances for account for date range
        balances = session.query(TableBalance).filter(TableBalance.account_key == account_id).all()
        running_balance = 0
        for i in range(len(formatted_transactions)):
            # First, skip any entry that's not a parent of a split
            if not formatted_transactions[i]['is_split_parent']:
                continue
            # The most recent transaction is the first entry in this list.
            # Since the balance amounts are effectively the last entry of the day's balance_after,
            #   we do nothing for the first entry
            transaction_date = formatted_transactions[i]['transaction_date']
            transaction_total = formatted_transactions[i]['total'] * -1
            if i == 0:
                running_balance = next(x.amount for x in balances if x.date == transaction_date)
            # Carry forward the balance from the last transaction, then calculate the next transaction's balance.
            formatted_transactions[i]['balance_after'] = running_balance
            running_balance += transaction_total

        return formatted_transactions

    @classmethod
    def add_transaction_split(cls, session: Session, data: ModelDictType) -> TableTransactionSplit:
        return cls._add_obj(session=session, obj_class=TableTransactionSplit, data=data)

    @classmethod
    def get_transaction_split(cls, session: Session, transaction_split_id: int = None,
                              filters: FilterListType = None) -> TableTransactionSplit:
        if filters is None:
            filters = [TableTransactionSplit.transaction_split_id == transaction_split_id]
        return cls._get_obj(session=session, obj_class=TableTransactionSplit, filters=filters)

    @classmethod
    def get_transaction_splits(cls, session: Session, filters: FilterListType = None,
                               limit: int = 100) -> List[TableTransactionSplit]:
        return cls._get_objs(session=session, obj_class=TableTransactionSplit, filters=filters, limit=limit)

    @classmethod
    def edit_transaction_split(cls, session: Session, transaction_split_id: int, data: ModelDictType):
        transaction_split_obj = cls.get_transaction_split(session=session, transaction_split_id=transaction_split_id)

        cls._edit_obj(session=session, obj=transaction_split_obj, data=data)


if __name__ == '__main__':
    from senditark_api.config import DevelopmentConfig

    DevelopmentConfig.build_db_engine()
    session = DevelopmentConfig.SESSION()
    tq = TransactionQueries
    account = session.query(TableAccount).filter(TableAccount.account_id == 2).one_or_none()
    tq.get_all_transaction_splits(session=session, acct=account, as_sum=False)
