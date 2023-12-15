from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///songs.sqlite"
app.config["SECRET_KEY"] = '8af126e22aacd3584bb381f2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = 'filesystem'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
Session(app)
app.app_context().push()

from . import database
from . import controller
from . import models

if __name__ == "__main__":
    app.run(debug=True)
