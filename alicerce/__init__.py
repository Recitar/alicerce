from flask import Flask
from alicerce.alicerce_api.api import api_bp
from alicerce.webpage import site_bp
from alicerce.ext import config

def create_app():
    """Cria uma aplicação flask

    Returns:
        Flask: objeto flask criado
    """
    app = Flask(__name__)
    app.register_blueprint(api_bp)
    app.register_blueprint(site_bp)
    config.init_app(app)
    return app