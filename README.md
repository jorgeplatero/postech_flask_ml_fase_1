# API Flask para Predição de Espécies Iris

Esta é uma API RESTful construída com Flask que utiliza um modelo de Machine Learning (ML) treinado para prever espécies de Iris. A API é protegida por autenticação via JSON Web Token (JWT) e armazena o histórico de predições em um banco de dados SQLite usando SQLAlchemy.

### ⚙️ Pré-requisitos

Certifique-se de ter o Python 3.x instalado.

###  📦 Instalação

Clone o repositório e instale as dependências listadas no requirements.txt:

```bash
git clone [URL_DO_SEU_REPOSITORIO]
cd [NOME_DO_SEU_REPOSITORIO]
pip install -r requirements.txt
```

### 📂 Estrutura do Projeto

O projeto deve conter os seguintes arquivos na raiz:
Arquivo	Descrição
ml_api.py	O código-fonte principal da API Flask (o código fornecido).
requirements.txt	Lista de dependências (Flask, joblib, numpy, SQLAlchemy, pyjwt).
model_iris.pkl	O modelo de ML treinado (necessário para as predições).
predictions.db	O banco de dados SQLite (será criado na primeira execução).
vercel.json	(Opcional) Arquivo de configuração para deploy no Vercel.

### ▶️ Como Rodar a Aplicação Localmente

Execute o script Python diretamente:

```bash
python ml_api.py
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
    "message": "API de Predição Iris está rodando. Acesse /apidocs para documentação.",
    "status": "online"
}
```

2. Login (/login)

Use este endpoint para obter um token de acesso.

- Método: POST
- Corpo da requisição (JSON):

```json
{
    "username": "admin",
    "password": "secret"
}
```

Resposta de sucesso (JSON):

```json
    {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpX..."
    }
```

3. Predição (/predict)

Endpoint protegido que recebe os parâmetros da flor e retorna a classe prevista, além de armazenar o registro no banco de dados (predictions.db).

- Método: POST
- Header: Authorization: Bearer [TOKEN_RECEBIDO]
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
        "predicted_class": 0
    }
```

4. Histórico de Predições (/predictions)

Endpoint protegido que lista as predições armazenadas.

- Método: GET
- Header: Authorization: Bearer [TOKEN_RECEBIDO]
- Parâmetros de Query (Opcional):
    - limit (int): máximo de registros a retornar (padrão: 10).
    - offset (int): posição inicial dos registros (padrão: 0).
- Exemplo: /predictions?limit=5&offset=10
- Resposta de sucesso (JSON): uma lista de objetos de predição.

### ☁️ Deploy no Vercel

Esta API está configurada para Deploy Serverless no Vercel utilizando o runtime @vercel/python.

Para realizar o deploy, certifique-se de que o arquivo vercel.json esteja na raiz, apontando para ml_api.py como fonte principal. O Vercel gerenciará o ambiente com base no requirements.txt.

### 🛡️ Segurança e Configuração

- JWT Secret: altere a variável JWT_SECRET = 'MEUSEGREDOAQUI' para uma chave forte e armazene-a como variável de ambiente em produção (e.g., Vercel Environment Variables).
- Banco de Dados: o SQLite (predictions.db) é ideal para desenvolvimento e Vercel Serverless. Para produção em larga escala, considere migrar para um banco de dados externo (PostgreSQL, MySQL, etc.).