from comunidadeimpressionadora import database, login_manager
from datetime import datetime
from flask_login import UserMixin


# Função que fará o login
@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario)) # O .get() procura pela primary_key

# Class usuário criada que tem como herança a classe database criada
class Usuario(database.Model, UserMixin):
    # Informa o tipo de dado. Por ser chave primária, não haverá nenhuma outra igual a ela na tabela e ela será preenchida automaticamente
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    senha = database.Column(database.String, nullable=False)
    foto_perfil = database.Column(database.String, default='default.jpg')
    cursos = database.Column(database.String, nullable=False, default='Não Informado')

    # Relação entre as tabelas Usuários/Post. Nome da tabela puxada, como ver o autor(post.Autor), puxa todas as informações do autor
    posts = database.relationship('Post', backref='Autor', lazy=True)
    comentario = database.relationship('Comentario', backref='Autor', lazy=True)

    def contar_posts(self):
        return len(self.posts)

class Post(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    titulo = database.Column(database.String, nullable=False)
    corpo = database.Column(database.Text, nullable=False)
    curtidas = database.Column(database.Integer, nullable=False, default=0)

    # Chama a função utcnow que rodará sempre quando um post é criado
    data_criacao = database.Column(database.DateTime, nullable=False, default=datetime.utcnow())

    # Chave que vai fazer a conexão com 1 - Muitos, Classe.Coluna(a classe sempre deve ser minúscula aqui)
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)
    id_usuarios_curtidas = database.Column(database.String, default='')
    comentarios = database.relationship('Comentario', backref='Post', lazy=True)

    def adicionar_id_usuario(self, id_usuario, tipo):
        lista_ids_usauarios = self.id_usuarios_curtidas.split(',')
        if tipo=='adicionar':
            lista_ids_usauarios.append(str(id_usuario))
            self.curtidas += 1
        elif tipo=='remover':
            lista_ids_usauarios.remove(str(id_usuario))
            self.curtidas -= 1
        self.id_usuarios_curtidas = ','.join(lista_ids_usauarios)

class Comentario(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    corpo = database.Column(database.Text, nullable=False)
    curtidas = database.Column(database.Integer, nullable=False, default=0)
    data_criacao = database.Column(database.DateTime, nullable=False, default=datetime.utcnow())
    id_post = database.Column(database.Integer, database.ForeignKey('post.id'), nullable=False)
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)
    id_usuarios_curtidas = database.Column(database.String, default='')

    def adicionar_id_usuario(self, id_usuario, tipo):
        lista_ids_usauarios = self.id_usuarios_curtidas.split(',')
        if tipo=='adicionar':
            lista_ids_usauarios.append(str(id_usuario))
            self.curtidas += 1
        elif tipo=='remover':
            lista_ids_usauarios.remove(str(id_usuario))
            self.curtidas -= 1
        self.id_usuarios_curtidas = ','.join(lista_ids_usauarios)
