from flask import (
    Blueprint,
    jsonify,
    request,
)

from senditark_api.routes.helpers import get_session
from senditark_api.utils.query import SenditarkQueries as Query

bp_trans = Blueprint('transaction', __name__, url_prefix='/transaction')


@bp_trans.route('/all', methods=['GET'])
def get_all_transactions():
    session = get_session()
    transactions = Query.get_transactions(session=session)
    return jsonify(transactions), 200


@bp_trans.route('/add', methods=['POST'])
def add_transaction():
    pass
    # session = get_session()
    # data = request.get_json(force=True)

    # TODO: This line is part of an alternate method:
    #   Take out splits before adding the transaction, make splits individually
    #   and bind them to the transaction object
    # splits = data.pop('splits', [])
    # new_transaction = Query.add_transaction(session=session, data=data)

    # for split in splits:
    #     new_split = Query
    #
    #
    # return jsonify({
    #     'success': True,
    #     'message': f'Transaction {new_transaction} successfully added!'
    # }), 200


@bp_trans.route('/by-account/<int:account_id>/', methods=['GET'])
def get_transactions_by_account(account_id: int):
    session = get_session()
    transaction_data = Query.get_transaction_data_by_account(session=session, account_id=account_id)

    return jsonify(transaction_data), 200


@bp_trans.route('/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id: int):
    session = get_session()
    transaction = Query.get_transaction(session=session, transaction_id=transaction_id)
    return jsonify(transaction), 200


@bp_trans.route('/<int:transaction_id>/edit', methods=['GET', 'POST'])
def edit_transaction(transaction_id: int):
    session = get_session()
    if request.method == 'GET':
        transaction = Query.get_transaction(session=session, transaction_id=transaction_id)
        return jsonify(transaction), 200
    elif request.method == 'POST':
        data = request.get_json(force=True)
        transaction = Query.edit_transaction(session=session, transaction_id=transaction_id, data=data)
        return jsonify(transaction), 200


@bp_trans.route('/<int:transaction_id>/delete', methods=['DELETE'])
def delete_transaction(transaction_id: int):
    session = get_session()
    Query.delete_transaction(session=session, transaction_id=transaction_id)
    return jsonify({
        'success': True,
        'message': f'Transaction with id {transaction_id} successfully deleted.'
    }), 200
