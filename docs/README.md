# API Flask para Predição de Espécies Iris

Esta é uma API RESTful construída com Flask que utiliza um modelo de Machine Learning (ML) treinado para prever espécies de Iris. A API é protegida por autenticação via JSON Web Token (JWT) e armazena o histórico de predições em um banco de dados SQLite usando SQLAlchemy.

### ⚙️ Pré-requisitos

Certifique-se de ter o Python 3.x e o Poetry instalados em seu sistema.

Para instalar o Poetry, use o método oficial:

```bash
curl -sSL [https://install.python-poetry.org](https://install.python-poetry.org) | python3 -
```

###  📦 Instalação

Clone o repositório e instale as dependências listadas no requirements.txt:

```bash
git clone https://github.com/jorgeplatero/postech_flask_ml_fase_1.git
cd postech_flask_ml_fase_1
poetry install
```

O Poetry criará um ambiente virtual isolado e instalará todas as bibliotecas necessárias.

### 📂 Estrutura do Projeto

O projeto deve conter os seguintes arquivos na raiz:

* **`api.py`**: O arquivo principal da aplicação **Flask**, onde as rotas (endpoints da API) são definidas.
* **`config.py`**: Contém variáveis de configuração para diferentes ambientes (desenvolvimento, produção).
* **`model.pkl`**: O modelo de machine learning serializado (neste caso, para a classificação Iris).
* **`models.py`**: Contém a lógica de definição e interação com os dados, ou as classes/funções relacionadas ao modelo de ML.

### ▶️ Como Rodar a Aplicação Localmente

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
    "message": "Bem-vindo à API de predição Iris. Acesse /apidocs para documentação.",
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

5. Histórico de Predições (/predictions)

Endpoint protegido que lista as predições armazenadas.

- Método: GET
- Header: Authorization: Bearer [TOKEN]
- Parâmetros de query (opcional):
    - limit (int): máximo de registros a retornar (padrão: 10).
    - offset (int): posição inicial dos registros (padrão: 0).
- Exemplo: /predictions?limit=5&offset=10
- Resposta de sucesso (JSON): uma lista de objetos de predição.

### ☁️ Deploy no Vercel

Esta API está configurada para Deploy Serverless no Vercel utilizando o runtime @vercel/python.

Para realizar o deploy, certifique-se de que o arquivo vercel.json esteja na raiz, apontando para api.py como fonte principal. O Vercel gerenciará o ambiente com base no pyproject.toml.

### 🛡️ Segurança e Configuração

- JWT Secret: altere a variável JWT_SECRET para uma chave forte e armazene-a como variável de ambiente em produção (e.g., Vercel Environment Variables).
- Banco de dados: para produção, considere migrar para um banco de dados externo (PostgreSQL, MySQL, etc.).