from comunidadeimpressionadora import app
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import secrets
import os
from PIL import Image

def enviar_email(email_destino):
    global chave
    chave = random.randint(100000, 999999)
    corpo_email = f"""
    Código de confirmação de email: {chave}\n
    """
    msg = MIMEMultipart()
    msg['Subject'] = "Confirmação de email"
    msg['From'] = 'pedrovbittencourt@gmail.com'
    msg['To'] = email_destino
    password = 'speaodkjrwxkqjnb'
    msg.attach(MIMEText(corpo_email, 'html'))
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(msg['From'], password)
    s.sendmail(msg['From'], msg['To'], msg.as_string().encode('utf-8'))
    s.quit()
    return chave

def atualizar_cursos(form):
    lista_campos = []
    for campo in form:
        if 'curso_' in campo.name and campo.data:
            lista_campos.append(campo.label.text)
    if len(lista_campos) >= 1:
        return '; '.join(lista_campos)
    else:
        return 'Não Informado'


def salvar_imagem(imagem):
    # Adcionar o código no nome da imgaem
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)

    # Compactar a imagem
    tamanho = (400, 400)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)

    # Salvar a imagem
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo

def verificar_se_usuario_curtiu(id_usuario, id_usuarios):
    lista_ids_usuarios = id_usuarios.split(',')
    if id_usuario in lista_ids_usuarios:
        return False
    else:
        return True