# Manos Academia

Sistema de cadastro de planos de academia, feito com Flask e PostgreSQL.

## Como rodar o projeto

### 1. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 2. Conferir o usuário e senha no pgAdmin

1. Abra o **pgAdmin**.
2. No menu à esquerda, clique em **Servers** e depois no seu servidor local (normalmente já vem chamado de "PostgreSQL 15" ou parecido).
3. Ele vai pedir a **senha** que é postgres — essa é a senha que você definiu quando instalou o PostgreSQL. Anote ela.
4. O usuário padrão é sempre **postgres**, a não ser que você tenha criado outro.

Agora abra o `app.py` e o `criar_banco.py` no VS Code e confira se esses dados batem com o que você anotou:

```python
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
```

Se a sua senha do pgAdmin for diferente de `postgres`, troque o valor de `DB_PASSWORD` **nos dois arquivos**.

### 3. Criar o banco de dados (passo obrigatório!)

Antes de rodar o site, execute no terminal:

```bash
python criar_banco.py
```

Esse comando cria o banco `academia` e as tabelas. **Se você pular esse passo, o site vai dar erro dizendo que as tabelas não existem.**

Pra confirmar que funcionou, volte no pgAdmin, clique com o botão direito em **Databases** e escolha **Refresh**. Deve aparecer um banco novo chamado `academia`. Se você expandir ele (Databases → academia → Schemas → public → Tables), vai ver as tabelas `plano`, `unidade` e `modalidade` já criadas.

### 4. Rodar o site

```bash
python app.py
```

Depois é só abrir no navegador: **http://localhost:5000**