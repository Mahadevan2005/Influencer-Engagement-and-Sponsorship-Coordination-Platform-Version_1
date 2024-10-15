from flask import Flask 
from flask_login import LoginManager
import datetime
from application.database import db
app = None
login_manager =  LoginManager()

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SECRET_KEY'] = 'secretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///iescpdata.sqlite3"
    db.init_app(app)
    my_login_manager = LoginManager()
    my_login_manager.init_app(app)
    from application.models import User

    @my_login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    app.app_context().push()
    
    return app
app = create_app()

from application.routes import *

if __name__ == "__main__":
    app.run()