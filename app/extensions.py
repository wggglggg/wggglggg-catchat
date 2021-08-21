from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_moment import Moment
from flask_wtf.csrf import CSRFProtect


db = SQLAlchemy()
login_manager = LoginManager()
moment = Moment()
csrf = CSRFProtect()


@login_manager.user_loader
def load_load(user_id):
    from app.models import User
    return User.query.get(int(user_id))