# -------------------- CONFIGURAÇÃO DO SITE --------------------

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

# Configura a chave de segurança e o banco de dados
app.config['SECRET_KEY'] = 'b3e91ee560e9c76912bb02ebc2622bb2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dados_do_site.db'

database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'alert-info'

# Fica em baixo porque os routes têm que ficar em baixo do app
from comunidadeimpressionadora import routes