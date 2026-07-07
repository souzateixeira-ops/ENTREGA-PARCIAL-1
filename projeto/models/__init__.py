from flask_sqlalchemy import SQLAlchemy

# Isso aqui é tipo o "controle remoto" que a gente vai usar
# em todos os models pra falar com o banco de dados.
# Só existe UM db pra esse projeto inteiro.
db = SQLAlchemy()

# Importa as classes lá de baixo (depois de criar o "db" ali em cima)
# pra elas ficarem registradas e o Flask saber que essas tabelas existem.
from models.unidade import Unidade
from models.modalidade import Modalidade
from models.plano import Plano