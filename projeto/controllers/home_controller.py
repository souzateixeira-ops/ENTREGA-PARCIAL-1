from flask import Blueprint, render_template

# Um Blueprint é tipo um "grupo de rotas". Em vez de deixar tudo
# solto dentro do app.py, a gente separa por assunto.
# Esse aqui cuida só da página inicial.
home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    return render_template('home.html')