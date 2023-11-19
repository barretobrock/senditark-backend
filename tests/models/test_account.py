from random import randint
from unittest import TestCase

from senditark_api.model.account import (
    AccountType,
    Currency,
    TableAccount,
)

from ..common import random_string


class TestTableAccount(TestCase):

    def setUp(self):
        self.tbl_1 = {
            'name': random_string(10).upper(),
            'account_type': AccountType(randint(1, len(AccountType))),
            'account_currency': Currency(randint(1, len(Currency))),
            'parent_account': None,
        }
        self.tbl_2 = {
            'name': random_string(10).upper(),
            'account_type': self.tbl_1['account_type'],
            'account_currency': self.tbl_1['account_currency']
        }
        self.tbl_3 = {
            'name': random_string(20).upper(),
            'account_type': self.tbl_1['account_type'],
            'account_currency': self.tbl_1['account_currency']
        }

    def test_init(self):
        tbl_acct = TableAccount(**self.tbl_1)
        for k, v in self.tbl_1.items():
            self.assertEqual(v, getattr(tbl_acct, k))

    def test_parents(self):
        tbl_acct1 = TableAccount(**self.tbl_1)
        tbl_acct2 = TableAccount(parent_account=tbl_acct1, **self.tbl_2)
        tbl_acct3 = TableAccount(parent_account=tbl_acct2, **self.tbl_3)

        self.assertEqual(
            f'{self.tbl_1["account_type"].name}.{tbl_acct1.name}.{tbl_acct2.name}',
            tbl_acct2.full_name
        )
        self.assertEqual(
            f'{self.tbl_1["account_type"].name}.{tbl_acct1.name}.{tbl_acct2.name}.{tbl_acct3.name}',
            tbl_acct3.full_name
        )

    def test_parents_name_change(self):
        tbl_acct1 = TableAccount(**self.tbl_1)
        tbl_acct2 = TableAccount(parent_account=tbl_acct1, **self.tbl_2)
        tbl_acct3 = TableAccount(parent_account=tbl_acct2, **self.tbl_2)

        tbl_acct1.name = 'CHANGED'
        self.assertEqual(
            f'{self.tbl_1["account_type"].name}.{tbl_acct1.name}.{tbl_acct2.name}.{tbl_acct3.name}',
            tbl_acct3.full_name
        )
