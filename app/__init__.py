from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS, cross_origin


app = Flask(__name__)
app.config.from_object('config')
CORS(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

from app import views
