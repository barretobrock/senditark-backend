from flask import (
    Blueprint,
    jsonify,
    request,
)

from senditark_api.routes.helpers import get_session
from senditark_api.utils.query import SenditarkQueries as Query

bp_acct = Blueprint('account', __name__, url_prefix='/account')


@bp_acct.route('/all', methods=['GET'])
def get_all_accounts_with_balances():
    """This is used when displaying accounts"""
    accounts_with_balances = Query.get_accounts_with_balance(get_session())
    return jsonify(accounts_with_balances), 200


@bp_acct.route('/list', methods=['GET'])
def get_all_accounts():
    """This is used when you just need a list of names e.g., for a datalist"""
    accounts = Query.get_accounts(get_session())
    return jsonify(accounts), 200


@bp_acct.route('/add', methods=['POST'])
def add_account():
    session = get_session()
    data = request.get_json(force=True)

    new_acct = Query.add_account(session=session, data=data)

    return jsonify({
        'success': True,
        'message': f'Account "{new_acct.name}" ({new_acct.account_id}) successfully added!'
    }), 200


@bp_acct.route('/<int:account_id>', methods=['GET'])
def get_account_info(account_id: int):
    session = get_session()
    account = Query.get_account(session, account_id=account_id)
    transaction_splits = Query.get_transaction_data_by_account(session, account_id=account_id)
    # scheduled_splits = Query.get_
    return jsonify({
        'account': account,
        'transaction_splits': transaction_splits,
        'scheduled_splits': [],
    }), 200


@bp_acct.route('/<int:account_id>/edit', methods=['GET', 'POST'])
def edit_account_info(account_id: int):
    session = get_session()
    if request.method == 'GET':
        account = Query.get_account(session=session, account_id=account_id)
        return jsonify(account), 200
    elif request.method == 'POST':
        account = Query.edit_account(session=session, account_id=account_id, data=request.get_json(force=True))
        return jsonify(account), 200


@bp_acct.route('/<int:account_id>/reconcile', methods=['GET', 'POST'])
def get_reconcile_info(account_id: int):
    # session = get_session()
    # TODO: for GET: maybe just pull transaction splits (split-level to help dissect combi transactions) ?
    #   for POST: send only transaction ids that were locked?
    # account_recon = Query.get_account_reconciliation_info(session=session, account_id=account_id)
    return jsonify({'message': 'TODO!'}), 200


@bp_acct.route('/<int:account_id>/delete', methods=['DELETE'])
def delete_account(account_id: int):
    session = get_session()
    Query.delete_account(session=session, account_id=account_id)
    return jsonify({
        'success': True,
        'message': f'Account with id {account_id} successfully deleted.'
    }), 200
