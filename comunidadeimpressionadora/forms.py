from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from comunidadeimpressionadora.models import Usuario
from flask_login import current_user

class FormCriarConta(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(8, 20)])
    confirmacao_senha = PasswordField('Confirmação da Senha', validators=[DataRequired(), EqualTo('senha')])
    button_submit_cadastro = SubmitField('Cadastrar')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('This e-mail already exists. Use another e-mail or sign in')
class FormLogin(FlaskForm):
    email = StringField('E-mail',validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(8, 20)])
    lembrar_dados = BooleanField('Lembrar Dados de Acesso')
    button_submit_login = SubmitField('Fazer Login')

class FormEditarPerfil(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    foto_perfil = FileField('Atualizar foto de Perfil', validators=[FileAllowed(['jpg','png'])])

    curso_excel = BooleanField('Excel Impressionador')
    curso_vba = BooleanField('VBA Impressionador')
    curso_powerbi = BooleanField('Powe BI Impressionador')
    curso_python = BooleanField('Python Impressionador')
    curso_sql = BooleanField('SQL Impressionador')
    curso_javascript = BooleanField('JavaScript Impressionador')

    button_submit_editarperfil = SubmitField('Confirmar Edição')

    def validate_email(self, email):
        # Verificar se o email foi alterado
        if current_user.email != email.data:
            # Verifica se esse email está ou não cadastrado
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError('E-mail já cadastrado. Cadastre outro e-mail')


class FormCriarPost(FlaskForm):
    titulo = StringField('Título do Post', validators=[DataRequired(), Length(2,140)])
    corpo = TextAreaField('Escreva seu Post aqui', validators=[DataRequired()])
    botao_submit = SubmitField('Criar Post')


# Essa função foi criada apenas para mudar o nome do botão de 'Criar Post' para 'Editar Post'
def criar_formulario_post(tipo='Criar Post'):
    class FormCriarPost2(FlaskForm):
        titulo = StringField('Título do Post', validators=[DataRequired(), Length(2,140)])
        corpo = TextAreaField('Escreva seu Post aqui', validators=[DataRequired()])
        botao_submit = SubmitField(tipo)
    return FormCriarPost2

class FormComentario(FlaskForm):
    corpo = TextAreaField('Escreva seu comentário aqui', validators=[DataRequired()])
    botao_submit = SubmitField('Postar Comentario')

def FormConfirmacaoEmail(codigo_enviado):
    class FormConfirmacaoEmail(FlaskForm):
        codigo = StringField('Código de confirmação enviado para o email informado', validators=[DataRequired()])
        botao_submit = SubmitField('Confirmar email')

        def validate_codigo(self, codigo):
            if codigo_enviado != int(codigo.data):
                raise ValidationError('Incorrect Code')

    return FormConfirmacaoEmail

class FormEnviarEmailRecuperacao(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    botao_submit = SubmitField('Enviar código de verificação')

    def validate_email(self, email):
        usuarios = Usuario.query.all()
        emails_cadastrados = [usuario.email for usuario in usuarios]
        if email.data not in emails_cadastrados:
            raise ValidationError('Esse email não está cadastrado')

class FormMudarSenha(FlaskForm):
    senha = PasswordField('Nova Senha', validators=[DataRequired(), Length(8, 20)])
    confirmacao_senha = PasswordField('Confirmação Nova Senha', validators=[DataRequired(), EqualTo('senha')])
    botao_submit = SubmitField('Alterar senha')