from flask import (
    Blueprint,
    jsonify,
    request,
)

from senditark_api.model.account import (
    AccountType,
    Currency,
    TableAccount,
)
from senditark_api.routes.helpers import get_db_conn
from senditark_api.utils.query_aid import SenditarkQueries

bp_acct = Blueprint('account', __name__, url_prefix='/account')


@bp_acct.route('/all', methods=['GET'])
def get_all_accounts():
    accounts = SenditarkQueries.get_accounts(get_db_conn())
    return jsonify({'accounts': accounts}), 200


@bp_acct.route('/<int:account_id>', methods=['GET'])
def get_account_info(account_id: int):
    account, transaction_splits = SenditarkQueries.get_account_info(get_db_conn(), account_id=account_id)
    return jsonify({'account': account, 'transaction_splits': transaction_splits}), 200


@bp_acct.route('/add', methods=['POST'])
def add_account():
    data = request.get_json()
    # TODO: Check account type, throw err when invalid

    new_acct = TableAccount(
        name=data.get('account_name'),
        account_type=AccountType[data.get('account_type')],
        account_currency=Currency[data.get('account_currency')],
        parent_account=None,
        is_hidden=False
    )

    # TODO: error handling -- what's thrown when a commit fails?
    sess = get_db_conn().session
    sess.add(new_acct)
    sess.commit()

    # TODO: Confirm that we can still see account after commit (I think it's preserved?)

    return jsonify({
        'success': True,
        'message': f'Account "{new_acct.name}" ({new_acct.account_id}) successfully registered!'}), 200


@bp_acct.route('/<int:account_id>/reconcile', methods=['GET'])
def get_reconcile_info(account_id: int):
    accounts = SenditarkQueries.get_account_reconiliation_info(get_db_conn(), account_id=account_id)
    return jsonify({'accounts': accounts})
