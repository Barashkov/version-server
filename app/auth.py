from flask import Blueprint
from flask_httpauth import HTTPBasicAuth
from app.config import Config
from app.utils.logger import get_logger

logger = get_logger(__name__)
auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    if username == Config.AUTH_USERNAME:
        return Config.AUTH_PASSWORD
    return None


@auth.error_handler
def unauthorized():
    return {'error': 'Unauthorized access'}, 401


def init_auth(app):
    app.extensions['auth'] = auth
