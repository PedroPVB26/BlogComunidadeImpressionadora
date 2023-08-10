# -------------------- CONFIGURAÇÃO DO SITE --------------------

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os
import sqlalchemy

app = Flask(__name__)

# Configura a chave de segurança e o banco de dados
# Pegando a variável de ambiente com o link para o banco de dados (se existir)
app.config['SECRET_KEY'] = 'b3e91ee560e9c76912bb02ebc2622bb2'

if os.getenv("DATABASE_URL"):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dados_do_site.db'

database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'alert-info'


from comunidadeimpressionadora import models
engine = sqlalchemy.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
inspector = sqlalchemy.inspect(engine)

if not inspector.has_table("usuario"):
    with app.app_context():
        database.drop_all()
        database.create_all()

# Fica em baixo porque os routes têm que ficar em baixo do app
from comunidadeimpressionadora import routes
