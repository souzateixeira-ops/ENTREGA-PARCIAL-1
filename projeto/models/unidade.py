from models import db

# Essa classe representa a tabela "unidade" no banco.
# Cada unidade é uma filial da academia (Centro, Zona Norte, Zona Sul...)
class Unidade(db.Model):
    __tablename__ = 'unidade'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False, unique=True)
    endereco = db.Column(db.String(200))

    # Isso não vira uma coluna no banco. É só um "atalho" pra gente
    # conseguir pegar todos os planos de uma unidade fazendo
    # unidade.planos, sem precisar escrever uma busca toda vez.
    planos = db.relationship('Plano', backref='unidade', lazy=True)