from dynaconf import FlaskDynaconf
import os

def init_app(app):
    FlaskDynaconf(app)
    app.config.load_extensions("EXTENSIONS")
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY", app.config["SECRET_KEY"]
    )
    app.config["JWT_SECRET_KEY"] = os.getenv(
        "JWT_SECRET_KEY", app.config["JWT_SECRET_KEY"]
    )

    
