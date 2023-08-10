from flask import render_template, redirect, url_for, flash, request, abort, session
from comunidadeimpressionadora import app, database, bcrypt
from comunidadeimpressionadora.funcoes import enviar_email, salvar_imagem, atualizar_cursos, verificar_se_usuario_curtiu
from comunidadeimpressionadora.forms import FormLogin, FormCriarConta, FormEditarPerfil, FormCriarPost, criar_formulario_post, FormComentario, FormConfirmacaoEmail, FormEnviarEmailRecuperacao, FormMudarSenha
from comunidadeimpressionadora.models import Usuario, Post, Comentario
from flask_login import login_user, logout_user, current_user, login_required
import os


@app.route('/')
def home():
    # .desc() serviu para ordenar dos post mais recentes para os mais antigos
    posts = Post.query.order_by(Post.id.desc())
    if current_user.is_authenticated:
        id_usuario_curtida = str(current_user.id)
    else:
        id_usuario_curtida = 0
    return render_template('home.html', posts=posts, id_usuario_curtida=id_usuario_curtida)


@app.route('/contato')
def contato():
    return render_template('contato.html')


@app.route('/usuarios')
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    # Vai tornanr possível a utilização da variável python 'lista_usuarios' no código html
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)


# Página de Login. Com os métodos 'GET'(padrão) e 'POST'(para permitir o envio de formulários pelos usuários) definidos
@app.route('/login', methods=['GET','POST'])
def login():
    form_login = FormLogin()

    # Se o usuário fizer o cadastro, quando ele for direcionado para cá o login não deve ser feito automaticamente,
    # o usuário deve preencher as informações de login (email e senha)


    if form_login.validate_on_submit() and 'button_submit_login' in request.form:
        # Fazendo o login
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f'Login feito com sucesso no e-mail {form_login.email.data}', 'alert-success')
            parametro_next = request.args.get('next')
            if parametro_next:
                return redirect(parametro_next)
            else:
                return redirect(url_for('home'))
        else:
            flash(f'Falha no login, emails ou senha incorretos', 'alert-danger')

    # Faz o logout para caso o usuário tenha vindo de 'confirmacao_email'
    logout_user()

    return render_template('login.html', form_login=form_login)


@app.route('/enviar_email_recuperacao', methods=['GET','POST'])
def enviar_email_recuperacao():
    form = FormEnviarEmailRecuperacao()

    if form.validate_on_submit():
        session['codigo_recuperacao'] = enviar_email(form.email.data)
        session['id_usuario'] = Usuario.query.filter_by(email=form.email.data).first().id
        return redirect(url_for('confirmar_codigo_recuperacao'))

    return render_template('enviar_email_recuperacao.html', form=form)


@app.route('/confirmar_codigo_recuperacao', methods=['GET','POST'])
def confirmar_codigo_recuperacao():
    codigo_enviado = session['codigo_recuperacao']
    form_1 = FormConfirmacaoEmail(codigo_enviado=codigo_enviado)
    form_confirmacao = form_1()
    if form_confirmacao.validate_on_submit():
        return redirect(url_for('mudar_senha'))

    return render_template('confirmar_codigo_recuperacao.html', form=form_confirmacao)


@app.route('/mudar_senha', methods=['GET','POST'])
def mudar_senha():
    form = FormMudarSenha()
    usuario = Usuario.query.get(session['id_usuario'])
    if form.validate_on_submit():
        senha_crypt = bcrypt.generate_password_hash(form.senha.data)
        usuario.senha = senha_crypt
        database.session.commit()
        flash(f'Senha do usuario {usuario.username} alterada com sucesso', 'alert-success')
        return redirect(url_for('login'))

    return render_template('mudar_senha.html',form=form)


@app.route('/cadastro', methods=['GET','POST'])
def cadastro():
    form_cadastro = FormCriarConta()

    if form_cadastro.validate_on_submit():
        senha_crypt = bcrypt.generate_password_hash(form_cadastro.senha.data)
        codigo_enviado = enviar_email(form_cadastro.email.data)
        session['codigo_confirmacao'] = codigo_enviado
        session['senha'] = senha_crypt
        return redirect(url_for('confirmacao_email', username=form_cadastro.username.data, email=form_cadastro.email.data))

    return render_template('cadastro.html', form_cadastro=form_cadastro)


@app.route('/cadastro/confirmar/<username>/<email>', methods=['GET','POST'])
def confirmacao_email(username, email):
    codigo_enviado = session['codigo_confirmacao']
    senha = session['senha']
    form_1 = FormConfirmacaoEmail(codigo_enviado=codigo_enviado)
    form_confirmacao = form_1()

    if form_confirmacao.validate_on_submit() and 'botao_submit' in request.form:
        usuario = Usuario(username=username, email=email, senha=senha)
        session.pop('codigo_confirmacao', None)
        session.pop('senha', None)
        database.session.add(usuario)
        database.session.commit()
        flash(f'Cadastro feito com sucesso no e-mail {email}', 'alert-success')
        return redirect(url_for('login'))

    return render_template('confirmarEmail.html', form_confirmacao=form_confirmacao)


@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash('Logout feito com sucesso','alert-success')
    return redirect(url_for('home'))


@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    return render_template('perfil.html', foto_perfil=foto_perfil)


@app.route('/perfil/<id_perfil>/excluir_perfil', methods=['GET','POST'])
@login_required
def excluir_perfil(id_perfil):
    perfil = Usuario.query.get(id_perfil)
    posts = Post.query.all()
    todos_comentarios = Comentario.query.all()
    if perfil == current_user:
        comentarios_usuario = Comentario.query.filter(Comentario.id_usuario==id_perfil).all()
        post_usuario = Post.query.filter(Post.id_usuario==id_perfil).all()

        # Excluindo os cometários que o usuário fez em outros posts
        for comentario in comentarios_usuario:
            database.session.delete(comentario)

        # Excluindo os posts dos usuário e os comentários dele
        for post in post_usuario:
            comentarios = Comentario.query.filter_by(id_post=post.id).all()
            for comentario in comentarios:
                database.session.delete(comentario)
            database.session.delete(post)

        # Excluindo as curtidas que o usuário deu nos posts e comentários
        for post in posts:
            if verificar_se_usuario_curtiu(str(id_perfil), post.id_usuarios_curtidas) == False:
                post.adicionar_id_usuario(id_usuario=id_perfil,tipo='remover')

        for comentario in todos_comentarios:
            if verificar_se_usuario_curtiu(str(id_perfil), comentario.id_usuarios_curtidas) == False:
                comentario.adicionar_id_usuario(id_usuario=id_perfil,tipo='remover')

        # Excluindo o usuário
        database.session.delete(current_user)
        database.session.commit()
        flash('Perfil excluído com sucesso','alert-danger')
        return redirect(url_for('home'))
    else:
        abort(403)


@app.route('/post/criar', methods=['GET','POST'])
@login_required
def criar_post():
    form = FormCriarPost()
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, corpo=form.corpo.data, Autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post criado com sucesso','alert-success')
        return redirect(url_for('home'))
    return render_template('criarpost.html', form=form)




@app.route('/perfil/editar', methods=['GET','POST'])
@login_required
def editar_perfil():
    form = FormEditarPerfil()
    if form.validate_on_submit():
        # Mudando o email e username do usuário
        current_user.email = form.email.data
        current_user.username = form.username.data

        # Mudando a foto de perfil
        if form.foto_perfil.data:
            # Excluindo a foto antiga antes de adicionar a nova
            caminho_completo_antigo = os.path.join(app.root_path, 'static/fotos_perfil', current_user.foto_perfil)
            if os.path.exists(caminho_completo_antigo) and current_user.foto_perfil != 'default.jpg':
                os.remove(caminho_completo_antigo)

            # Salvando a nova foto de perfil
            nome_imagem = salvar_imagem(form.foto_perfil.data)
            current_user.foto_perfil = nome_imagem

        # Adicionando os cursos
        current_user.cursos = atualizar_cursos(form)

        # Salvando no banco de dados
        database.session.commit()
        flash('Perfil atualizado com sucesso','alert-success')
        return redirect(url_for('perfil'))

    # Para quando o usuário entrar em editar perfil
    elif request.method == 'GET':
        # Campos preenchidos
        form.email.data = current_user.email
        form.username.data = current_user.username

        # Preencher os cursos que o usuário já preencheu
        for campo in form:
            if 'curso_' in campo.name:
                if campo.label.text in current_user.cursos:
                    campo.data = True

    # Pegando o lugar da foto e para mandar para o arquivo html
    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    return render_template('editar_perfil.html', foto_perfil=foto_perfil, form=form)

@app.route('/post/<post_id>', methods=['GET','POST'])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)
    comentarios = Comentario.query.filter_by(id_post=post_id).order_by(Comentario.id.desc()).all()

    # Editando o post
    if current_user == post.Autor:
        CriarPost2 = criar_formulario_post(tipo='Editar Post')
        form = CriarPost2()
        if request.method == 'GET':
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
        elif form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            database.session.commit()
            flash('Post Atualizado com Sucesso','alert-success')
            return redirect(url_for('home'))
    else:
        form = None

    # Comentário
    form_comentario = FormComentario()
    if form_comentario.validate_on_submit():
        comentario = Comentario(corpo=form_comentario.corpo.data, Post=post, Autor=current_user)
        database.session.add(comentario)
        database.session.commit()
        flash('Comentário criado com sucesso', 'alert-success')
        return redirect(f'/post/{post_id}')

    return render_template('post.html', post=post, form=form, form_comentario=form_comentario, comentarios=comentarios, id_usuario_curtida=str(current_user.id))


@app.route('/post/<post_id>/curtir/<carregar_para>', methods=['GET', 'POST'])
@login_required
def like_deslike_post(post_id, carregar_para):
    post = Post.query.get(str(post_id))

    if verificar_se_usuario_curtiu(str(current_user.id), post.id_usuarios_curtidas):
        post.adicionar_id_usuario(id_usuario=current_user.id, tipo='adicionar')
        database.session.commit()
        if 'home' == carregar_para:
            return redirect(url_for('home') + f'#{post_id}')
        if 'perfil' == carregar_para:
            return redirect(url_for('exibir_post', post_id=post_id))
    else:
        post.adicionar_id_usuario(id_usuario=current_user.id, tipo='remover')
        database.session.commit()
        if 'home' == carregar_para:
            return redirect(url_for('home') + f'#{post_id}')
        if 'perfil' == carregar_para:
            return redirect(url_for('exibir_post', post_id=post_id))


@app.route('/post/<post_id>/<comentario_id>/curtir_comentario', methods=['GET','POST'])
@login_required
def like_deslike_comentario(comentario_id, post_id):
    comentario = Comentario.query.get(comentario_id)

    if verificar_se_usuario_curtiu(str(current_user.id), comentario.id_usuarios_curtidas):
        comentario.adicionar_id_usuario(id_usuario=current_user.id, tipo='adicionar')
        database.session.commit()
        return redirect(url_for('exibir_post', post_id=post_id) + f'#{comentario_id}')
    else:
        comentario.adicionar_id_usuario(id_usuario=current_user.id, tipo='remover')
        database.session.commit()
        return redirect(url_for('exibir_post', post_id=post_id) + f'#{comentario_id}')


@app.route('/post/<post_id>/excluir_post', methods=['GET','POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    comentarios = Comentario.query.filter(Comentario.id_post == post_id).all()
    if current_user == post.Autor:
        for comentario in comentarios:
            database.session.delete(comentario)
        database.session.delete(post)
        database.session.commit()
        flash('Post Excluido com sucesso', 'alert-danger')
        return redirect(url_for('home'))
    else:
        # Erro que sinaliza uma ação proibida
        abort(403)

@app.route('/post/<post_id>/<comentario_id>/excluir_comentario', methods=['GET','POST'])
@login_required
def excluir_comentario(comentario_id, post_id):
    comentario = Comentario.query.get(comentario_id)
    if current_user == comentario.Autor:
        database.session.delete(comentario)
        database.session.commit()
        flash('Comentário excluído com sucesso', 'alert-danger')
        return redirect(f'/post/{post_id}')
    else:
        abort(403)