# API Flask para Predição de Espécies Iris

Esta é uma API RESTful construída com Flask que utiliza um modelo de Machine Learning (ML) treinado para prever espécies de Iris. A API é protegida por autenticação via JSON Web Token (JWT) e armazena o histórico de predições em um banco de dados SQLite usando SQLAlchemy.

### ⚙️ Pré-requisitos

Certifique-se de ter o Python 3.x e o Poetry instalados em seu sistema.

Para instalar o Poetry, use o método oficial:

```bash
curl -sSL [https://install.python-poetry.org](https://install.python-poetry.org) | python3 -
```

### 📦 Instalação

Clone o repositório e instale as dependências listadas no requirements.txt:

```bash
git clone https://github.com/jorgeplatero/postech_flask_ml_fase_1.git
cd postech_flask_ml_fase_1
poetry install
```

O Poetry criará um ambiente virtual isolado e instalará todas as bibliotecas necessárias.

### Tecnologias

A aplicação atua como a camada de serviço (API) que interage com o cliente e o banco de dados.

| Componente | Tecnologia | Versão (Especificada) | Descrição |
| :--- | :--- | :--- | :--- |
| **Backend/API** | **Flask** | `>=3.1.2, <4.0.0` | Framework Python leve para o desenvolvimento da API RESTful. |
| **Machine Learning** | **Scikit-learn** | `>=1.7.2, <2.0.0` | Biblioteca para o treinamento e carregamento do modelo de classificação Iris. |
| **Serialização de Modelo** | **Joblib** | `>=1.5.2, <2.0.0` | Utilizada para salvar e carregar eficientemente o modelo de ML treinado. |
| **Autenticação** | **Flask-JWT-Extended** | `>=4.7.1, <5.0.0` | Implementa a segurança por JSON Web Tokens. |
| **Criptografia (Senhas)** | **Flask-Bcrypt** | `>=1.0.1, <2.0.0` | Gerencia o *hashing* seguro de senhas de usuário. |
| **Persistência/ORM** | **Flask-SQLAlchemy** | `>=3.1.1, <4.0.0` | Camada ORM para interagir com o banco de dados (PostgreSQL/SQLite). |
| **Driver DB (Postgres)** | **psycopg2-binary** | `>=2.9.11, <3.0.0` | Driver para conexão com o banco de dados PostgreSQL (ex: Neo Serverless Postgres). |
| **Documentação** | **Flasgger** | `>=0.9.7.1, <0.10.0.0` | Cria a documentação Swagger/OpenAPI interativa para a API. |
| **Ambiente** | **Python** | `>=3.11, <4.0` | Versões compatíveis para a execução do projeto. |
| **Gerenciamento** | **Poetry** | `2.2.1` | Gerenciador de dependências, usado para construir e gerenciar o ambiente. |

---

### ▶️ Como Rodar a Aplicação

Execute o script Python:

```bash
poetry run python3 api.py
```

A API estará rodando em http://127.0.0.1:5000/

### 🔑 Autenticação e Endpoints

O acesso aos endpoints de predição e histórico (/predict e /predictions) requer um JWT válido.

1. Home (/)

Endpoint raiz da API com status e boas-vindas. Não requer autenticação.

- Método: GET

Resposta de sucesso (JSON):

```json
{
    "msg": "Bem-vindo à API de predição Iris. Acesse /apidocs para documentação.",
    "status": "online"
}
```

2. Register (/register)

Use este endpoint para criar uma nova conta de usuário no banco de dados.

- Método: POST
- Corpo da requisição (JSON):

```json
{
    "username": "usuario",
    "password": "senha"
}
```

Resposta de sucesso (JSON):

```json
{
    "msg": "Usuário criado com sucesso"
}
```

3. Login (/login)

Use este endpoint para obter um token de acesso.

- Método: POST
- Corpo da requisição (JSON):

```json
{
    "username": "usuario",
    "password": "senha"
}
```

Resposta de sucesso (JSON):

```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpX..."
    }
```

4. Predição (/predict)

Endpoint protegido que recebe os parâmetros da flor e retorna a espécie prevista, além de armazenar o registro no banco de dados (predictions.db).

- Método: POST
- Header: Authorization: Bearer [TOKEN]
- Corpo da requisição (JSON):

```json
{
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
}
```

Resposta de sucesso (JSON):

```json
    {
        "predicted_specie": "virginica"
    }
```

5. Histórico de predições (/predictions)

Endpoint protegido que lista as predições armazenadas.

- Método: GET
- Header: Authorization: Bearer [TOKEN]
- Parâmetros de query (opcional):
    - limit (int): máximo de registros a retornar (padrão: 10).
    - offset (int): posição inicial dos registros (padrão: 0).
- Exemplo: /predictions?limit=5&offset=10
- Resposta de sucesso (JSON): uma lista de objetos de predição.

### ☁️ Deploy no Vercel

Esta API está configurada para Deploy no Vercel. A persistência de dados (histórico de predições) foi utiliza o Neon Serverless PostgreSQL.

Para realizar o deploy, certifique-se de que o arquivo vercel.json esteja na raiz, apontando para api.py como fonte principal. O Vercel gerenciará o ambiente com base no pyproject.toml.

### 🛡️ Segurança e Configuração

- JWT Secret: altere a variável JWT_SECRET para uma chave forte e armazene-a como variável de ambiente em produção (e.g., Vercel Environment Variables).
