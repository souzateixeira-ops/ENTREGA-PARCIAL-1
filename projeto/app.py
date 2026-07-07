
import os
from flask import Flask, render_template
from models import db
from controllers.home_controller import home_bp
from controllers.plano_controller import plano_bp

# Pega o caminho da pasta onde esse arquivo está,
# pra funcionar independente de onde a gente rodar o projeto.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

# O flash() (mensagens de sucesso/erro) guarda a mensagem na sessão do
# usuário, e toda sessão do Flask precisa ser assinada com uma chave
# secreta. Sem isso, flash() não funciona.
# OBS: em um projeto real essa chave não ficaria "dura" no código,
# e sim numa variável de ambiente. Aqui deixamos fixa só pra simplificar.
app.config['SECRET_KEY'] = 'chave-secreta-academia-2024'

# Aqui a gente fala pro Flask onde fica o banco de dados.
# Ele vai criar (ou usar) o arquivo academia.db dentro da pasta database/
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database', 'academia.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Liga os dois "pacotes de rotas" que a gente criou
app.register_blueprint(home_bp)
app.register_blueprint(plano_bp)


# ---------------------------------------------------------------------
# TRATAMENTO DE ERROS
# ---------------------------------------------------------------------
# Sem isso, se alguém tentar acessar um plano com um ID que não existe
# (ex: /plano/999), o Flask mostra a página de erro padrão dele, que é
# feia e não combina com o resto do site. Com o errorhandler, a gente
# troca essa página por uma nossa, mantendo o mesmo layout.

@app.errorhandler(404)
def pagina_nao_encontrada(erro):
    # get_or_404() (usado no controller de plano) cai aqui quando
    # o ID buscado não existe no banco.
    return render_template('404.html'), 404


@app.errorhandler(500)
def erro_interno_do_servidor(erro):
    # Erro inesperado (ex: falha ao falar com o banco). Mostra uma
    # página amigável em vez do "traceback" técnico do Flask.
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)