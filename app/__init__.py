# Used to initialize the Flask application and load the configuration settings from config.py.

from flask import Flask
from .config import Config
from .extensions import db


def create_app():
    app = Flask(__name__)

    # Load configuration from config.py
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app
