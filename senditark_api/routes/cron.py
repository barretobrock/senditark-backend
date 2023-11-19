from flask import (
    Blueprint,
    jsonify,
)

bp_cron = Blueprint('cron', __name__, url_prefix='/cron')


@bp_cron.route('/', methods=['GET'])
def run_cron():
    return jsonify({
        'message': 'TODO!'
    })
