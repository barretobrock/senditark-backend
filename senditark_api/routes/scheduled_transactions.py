from flask import (
    Blueprint,
    jsonify,
)

bp_schtrans = Blueprint('scheduled_transaction', __name__, url_prefix='/scheduled_transaction')


@bp_schtrans.route('/all')
def get_all_scheduled_transaction():
    pass


@bp_schtrans.route('/<int:transaction_id>')
def get_scheduled_transaction(transaction_id: int):
    pass
    # invoice = SenditarkQueries.get_invoice(get_db_conn(), invoice_id=invoice_id)
    # invoice_splits = SenditarkQueries.get_invoice_splits(get_db_conn(), invoice_id=invoice_id)
    # return jsonify({
    #     'invoice': invoice,
    #     'invoice-splits': invoice_splits
    # })


@bp_schtrans.route('/by-account/<int:account_id>/')
def get_scheduled_transactions_by_account(account_id: int):
    # SenditarkQueries.get_transactions(get_db_conn(), account_id=account_id)

    # TODO: flatten transactions, sort first by transaction_id, then by transaction_split_id

    return jsonify({'msg': 'ok!'}), 200
