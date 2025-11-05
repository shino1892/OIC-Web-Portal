from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from flask_cors import CORS
from .routes import bp

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, origins=["http://localhost:3000"])
    db.init_app(app)

    app.register_blueprint(bp)

    return app
