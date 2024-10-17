from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

mongo = PyMongo()

def create_app():
    load_dotenv('.cred')
    app = Flask(__name__)
    app.config["MONGO_URI"] = os.getenv('url')

    mongo.init_app(app)

    from .users import users_bp
    from .bikes import bikes_bp
    from .emprestimos import emprestimos_bp

    app.register_blueprint(users_bp)
    app.register_blueprint(bikes_bp)
    app.register_blueprint(emprestimos_bp)

    return app