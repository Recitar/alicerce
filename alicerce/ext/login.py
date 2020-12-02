from flask_simplelogin import SimpleLogin

from alicerce.alicerce_api.models.user import User


def verify_login(user):
    """Valida o usuario e senha para efetuar o login"""
    username = user.get('username')
    password = user.get('password')
    if not username or not password:
        return False
    existing_user = User.find_by_username(username)
    if not existing_user:
        return False
    if existing_user.check_password(password) and existing_user.admin:
        return True
    return False


def init_app(app):
    SimpleLogin(app, login_checker=verify_login)