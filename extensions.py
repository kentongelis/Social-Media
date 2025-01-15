from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)

db = SQLAlchemy(app)

# Set up authentication

from models import User

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


bcrypt = Bcrypt(app)
