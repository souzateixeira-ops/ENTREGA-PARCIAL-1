# Manos Academia

Sistema de cadastro de planos de academia, feito com Flask e PostgreSQL, seguindo o padrão MVC (Model-View-Controller).

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

Agora abra o `app.py` no VS Code e confira se esses dados batem com o que você anotou:

```python
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
```

Se a sua senha do pgAdmin for diferente de `postgres`, troque o valor de `DB_PASSWORD`.

### 3. Rodar o site

Não é mais necessário criar o banco manualmente antes de rodar o projeto. Agora o `app.py` faz tudo isso sozinho: ele cria o banco `academia` (caso ainda não exista), cria as tabelas e já sobe o servidor.

Basta rodar:

```bash
python app.py
```

Depois é só abrir no navegador: **http://localhost:5000**

Se quiser confirmar que o banco foi criado corretamente, volte no pgAdmin, clique com o botão direito em **Databases** e escolha **Refresh**. Deve aparecer o banco `academia`. Se você expandir ele (Databases → academia → Schemas → public → Tables), vai ver as tabelas `plano`, `unidade` e `modalidade` já criadas.

## Estrutura do projeto (MVC)

O projeto está organizado seguindo o padrão MVC:

- **Model** — camada responsável pelas regras de acesso e manipulação dos dados no banco.
- **View** — os templates (HTML) que o usuário vê no navegador.
- **Controller** — a lógica que recebe as requisições, conversa com o Model e decide qual View retornar.

O `app.py` é o ponto de entrada da aplicação: ele inicializa o banco de dados automaticamente e conecta as rotas às camadas do MVC.
## Equipe:
- Thiago Rafael Araujo de Souza
- Tecio Jordão Araujo de Souza
- Jailson Sergio Santos Junior
- João Victor de Souza Teixeira

O projeto está organizado seguindo o padrão MVC:
