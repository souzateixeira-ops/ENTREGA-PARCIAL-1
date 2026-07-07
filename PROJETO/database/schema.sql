-- banco de dados: academia.db da MANOS ACADEMIA --
-- apaga e recria as tabelas do zero, já com dados de teste--

PRAGMA foreign_keys = ON;

-- apaga as tabelas se já existirem, para permitir recriar do zero --
DROP TABLE IF EXISTS plano;
DROP TABLE IF EXISTS unidade;
DROP TABLE IF EXISTS modalidade;

-- tabela das filiais --
CREATE TABLE unidade (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nome    TEXT NOT NULL UNIQUE,
    endereco TEXT
);

-- tabela das modalidades --
CREATE TABLE modalidade (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);

-- tabela dos planos
CREATE TABLE plano (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nome          TEXT NOT NULL,
    duracao       INTEGER NOT NULL,   -- em meses
    nivel         TEXT NOT NULL,
    preco         REAL NOT NULL,
    descricao     TEXT,
    unidade_id    INTEGER NOT NULL,
    modalidade_id INTEGER NOT NULL,
    FOREIGN KEY (unidade_id)    REFERENCES unidade(id),
    FOREIGN KEY (modalidade_id) REFERENCES modalidade(id)
);

-- dados de teste

INSERT INTO unidade (id, nome, endereco) VALUES
    (1, 'Manos Academia - Centro', NULL),
    (2, 'Manos Academia - Zona Norte', NULL),
    (3, 'Manos Academia - Zona Sul', NULL);

INSERT INTO modalidade (id, nome) VALUES
    (1, 'Musculação'),
    (2, 'Funcional'),
    (3, 'Crossfit'),
    (4, 'Pilates'),
    (5, 'Natação'),
    (6, 'Yoga'),
    (7, 'Lutas');

INSERT INTO plano (id, nome, duracao, nivel, preco, descricao, unidade_id, modalidade_id) VALUES
    (1, 'Plano Mensal Musculação', 1, 'Iniciante', 99.9,
        'Acesso livre à sala de musculação com acompanhamento básico, ideal para quem está começando.',
        1, 1),
    (2, 'Plano Trimestral Funcional', 3, 'Intermediário', 249.9,
        'Treinos funcionais em grupo, focados em resistência, força e mobilidade.',
        2, 2),
    (3, 'Plano Semestral Crossfit', 6, 'Avançado', 459.9,
        'Treinos de alta intensidade com box completo e acompanhamento de coach especializado.',
        1, 3),
    (4, 'Plano Anual Total Fit', 12, 'Todos os níveis', 899.9,
        'Acesso completo a todas as modalidades da unidade, com avaliação física trimestral.',
        3, 1);