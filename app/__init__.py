from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
import logging
import os

db = SQLAlchemy()


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    migrate = Migrate(app, db)

    os.makedirs('logs', exist_ok=True)

    logging.basicConfig(
        filename='logs/errors.log',
        level=logging.ERROR,
        format='%(asctime)s %(levelname)s %(message)s'
    )

    from app.routes import main

    app.register_blueprint(main)

    return app