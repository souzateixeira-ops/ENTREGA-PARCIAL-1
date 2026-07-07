from models import db

# Essa classe representa a tabela "plano" no banco.
# É o plano que a academia vende (mensal, trimestral, etc).
class Plano(db.Model):
    __tablename__ = 'plano'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    duracao = db.Column(db.Integer, nullable=False)   # duração em meses
    nivel = db.Column(db.String(50), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text)

    # Aqui ficam as duas FK (chave estrangeira). Em vez de escrever
    # o nome da unidade e da modalidade toda hora, o plano só guarda
    # o "id" de cada uma, e o banco garante que esse id existe de verdade
    # na tabela unidade e na tabela modalidade.
    unidade_id = db.Column(db.Integer, db.ForeignKey('unidade.id'), nullable=False)
    modalidade_id = db.Column(db.Integer, db.ForeignKey('modalidade.id'), nullable=False)

    # Atalho pra pegar plano.modalidade direto (sem precisar buscar
    # na tabela modalidade na mão toda vez).
    modalidade = db.relationship('Modalidade', backref='planos', lazy=True)
    # plano.unidade já existe também, criado lá no relationship do unidade.py
