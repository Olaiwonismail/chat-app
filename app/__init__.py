
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_bootstrap import Bootstrap4

from app.config import Config
from flask_cors import CORS



# Bootstrap()
db = SQLAlchemy()
bcrypt =Bcrypt()
socketio = SocketIO()
login_manager = LoginManager()
bootstrap=Bootstrap4()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'



def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    socketio.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    #app.app_context().push()
    CORS(app, supports_credentials=True)
    Migrate(app, db)

    from app.main.routes import main
    from app.users.routes import users
    from app.requests.routes import requests
    # from app.errors.handlers import errors

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(requests)

    return app
