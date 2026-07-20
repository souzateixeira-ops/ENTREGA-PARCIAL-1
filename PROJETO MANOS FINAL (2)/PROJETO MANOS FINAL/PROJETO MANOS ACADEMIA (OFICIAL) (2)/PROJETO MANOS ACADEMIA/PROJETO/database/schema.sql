-- banco de dados: academia (PostgreSQL) da MANOS ACADEMIA --
-- apaga e recria as tabelas do zero, já com dados de teste --

-- apaga as tabelas se já existirem, para permitir recriar do zero --
DROP TABLE IF EXISTS plano;
DROP TABLE IF EXISTS unidade;
DROP TABLE IF EXISTS modalidade;

-- tabela das filiais --
-- No SQLite usávamos "INTEGER PRIMARY KEY AUTOINCREMENT".
-- No PostgreSQL o equivalente é o tipo SERIAL, que já cria
-- automaticamente uma sequence pra gerar os ids.
CREATE TABLE unidade (
    id       SERIAL PRIMARY KEY,
    nome     TEXT NOT NULL UNIQUE,
    endereco TEXT
);

-- tabela das modalidades --
CREATE TABLE modalidade (
    id   SERIAL PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE
);

-- tabela dos planos --
-- No PostgreSQL as FOREIGN KEY já são obrigatórias por padrão
-- (não existe o PRAGMA foreign_keys do SQLite, aqui já vem ligado).
CREATE TABLE plano (
    id            SERIAL PRIMARY KEY,
    nome          TEXT NOT NULL,
    duracao       INTEGER NOT NULL,   -- em meses
    nivel         TEXT NOT NULL,
    preco         REAL NOT NULL,
    descricao     TEXT,
    unidade_id    INTEGER NOT NULL REFERENCES unidade(id),
    modalidade_id INTEGER NOT NULL REFERENCES modalidade(id)
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

-- Como inserimos os ids "na mão" acima, as sequences internas do
-- SERIAL (que geram o próximo id automaticamente) ficam desatualizadas.
-- Sem isso, o próximo INSERT sem id explícito (feito pelo app.py)
-- tentaria usar o id 1 de novo e daria erro de duplicidade.
SELECT setval('unidade_id_seq', (SELECT MAX(id) FROM unidade));
SELECT setval('modalidade_id_seq', (SELECT MAX(id) FROM modalidade));
SELECT setval('plano_id_seq', (SELECT MAX(id) FROM plano));
