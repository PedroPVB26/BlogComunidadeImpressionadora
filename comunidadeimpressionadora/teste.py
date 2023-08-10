from comunidadeimpressionadora import database, app

with app.app_context():
    database.create_all()