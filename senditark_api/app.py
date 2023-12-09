from flask import (
    Flask,
    jsonify,
    request,
)
from flask_cors import CORS
from pukr import (
    InterceptHandler,
    get_logger,
)
from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES

from senditark_api.config import DevelopmentConfig
from senditark_api.flask_base import db
from senditark_api.routes.account import bp_acct
from senditark_api.routes.budget import bp_budg
from senditark_api.routes.cron import bp_cron
from senditark_api.routes.helpers import (
    get_app_logger,
    log_after,
    log_before,
)
from senditark_api.routes.invoice import bp_invc
from senditark_api.routes.main import bp_main
from senditark_api.routes.payee import bp_payee
from senditark_api.routes.scheduled_transactions import bp_schtrans
from senditark_api.routes.tags import bp_tag
from senditark_api.routes.transactions import bp_trans

ROUTES = [
    bp_acct,
    bp_budg,
    bp_cron,
    bp_invc,
    bp_main,
    bp_payee,
    bp_schtrans,
    bp_tag,
    bp_trans
]


def handle_err(err):
    _log = get_app_logger()
    _log.error(err)
    if err.code == 404:
        _log.error(f'Path requested: {request.path}')

    if isinstance(err, HTTPException):
        err_msg = getattr(err, 'description', HTTP_STATUS_CODES.get(err.code, ''))
        return jsonify({'message': err_msg}), err.code
    if not getattr(err, 'message', None):
        return jsonify({'message': 'Server has encountered an error.'}), 500
    return jsonify(**err.kwargs), err.http_status_code


def set_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
    return response


def create_app(*args, **kwargs) -> Flask:
    """Creates a Flask app instance"""
    # Config app, default to development if not provided
    config_class = kwargs.pop('config_class', DevelopmentConfig)
    config_class.build_db_engine()

    app = Flask(__name__, static_url_path='/')
    CORS(app)
    app.config.from_object(config_class)

    # Initialize database ops
    db.init_app(app)

    # Initialize logger
    logger = get_logger(app.config.get('NAME'), log_dir_path=app.config.get('LOG_DIR'),
                        show_backtrace=app.config.get('DEBUG'), base_level=app.config.get('LOG_LEVEL'))
    logger.info('Logger started. Binding to app handler...')
    app.logger.addHandler(InterceptHandler(logger=logger))
    # Bind logger so it's easy to call from app object in routes
    app.extensions.setdefault('logg', logger)

    # Register routes
    logger.info('Registering routes...')
    for ruut in ROUTES:
        app.register_blueprint(ruut)

    for err_code, name in HTTP_STATUS_CODES.items():
        if err_code >= 400:
            try:
                app.register_error_handler(err_code, handle_err)
            except ValueError as e:
                logger.debug(f'Bypassed exception registration on code {err_code} ({name}). Reason: {e}')

    app.config['db'] = db

    app.before_request(log_before)
    app.after_request(log_after)
    app.after_request(set_headers)

    return app
