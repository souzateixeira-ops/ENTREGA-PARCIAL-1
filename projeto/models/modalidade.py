from models import db

# Essa classe representa a tabela "modalidade" no banco.
# Modalidade é o tipo de treino: Musculação, Crossfit, Yoga, etc.
class Modalidade(db.Model):
    __tablename__ = 'modalidade'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False, unique=True)