# Binance Trading Bot API

Esta é uma API REST baseada em FastAPI para gerenciar um bot de trading na Binance. A API fornece endpoints para gerenciamento de usuários, configuração, rastreamento de tickers, transações e relatórios de desempenho.

## Alunos
|Matrícula | Aluno |
| -- | -- |
| 202208385036 | Bernardo Pinto |
| 202307164641 | Gabriel Mendes |
| 202208385011 | Matheus Peçanha |

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following content:
```
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/binance_trading_bot
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
```

Replace `your_password` with your MySQL password and generate a secure `SECRET_KEY`.

4. Run the application:
```bash
uvicorn main:app --reload
```

## API Endpoints

### Autenticação
- `POST /token` - Obter token de acesso (login)

### Gerenciamento de Usuários
- `POST /users/` - Criar novo usuário
- `GET /users/me/` - Obter informações do usuário atual
- `GET /users/{user_id}` - Obter informações de um usuário específico
#teste

### Configuração do Usuário
- `POST /users/me/configuration/` - Criar configuração do usuário
- `GET /users/me/configuration/` - Obter configuração do usuário
- `POST /users/{user_id}/configurations/` - Criar configuração para um usuário específico
- `GET /users/{user_id}/configurations/` - Obter configuração de um usuário específico

### Rastreamento de Tickets
- `POST /users/me/tracking-tickers/` - Adicionar novo ticker para rastreamento
- `GET /users/me/tracking-tickers/` - Obter todos os tickers rastreados
- `DELETE /users/me/tracking-tickers/{ticker_id}` - Excluir um ticker rastreado
- `POST /users/{user_id}/tracking-tickers/`- Adicionar ticker para um usuário específico
- `GET /users/{user_id}/tracking-tickers/` - Obter tickers de um usuário específico
- `DELETE /users/{user_id}/tracking-tickers/{ticker_id}` - Excluir ticker de um usuário específico

### Transações
- `POST /users/{user_id}/transactions/` - Criar nova transação
- `GET /users/{user_id}/transactions/` - Obter transações de um usuário (com filtros de data opcional)

### Relatórios de Desempenho
- `GET /users/me/reports/` - Obter relatórios de desempenho do usuário atual

### Dados de Mercado
- `GET /prices/{symbol}` - Obter preço atual de um símbolo
- `GET /prices/klines/{symbol}` - Obter dados históricos (candles) de um símbolo

### Documentação da API
Uma vez que a aplicação esteja em execução, você pode acessar:

- Documentação interativa da API em: `http://localhost:8000/docs`
- Documentação alternativa da API em: `http://localhost:8000/redoc`

## Example Usage

1. Create a new user:
```bash
curl -X POST "http://localhost:8000/users/" -H "Content-Type: application/json" -d '{
  "login": "user@example.com",
  "password": "strongpassword",
  "binanceApiKey": "your-binance-api-key",
  "binanceSecretKey": "your-binance-secret-key",
  "saldoInicio": 1000.0
}'
```

2. Get access token:
```bash
curl -X POST "http://localhost:8000/token" -d "username=user@example.com&password=strongpassword"
```

3. Create user configuration (requires authentication):
```bash
curl -X POST "http://localhost:8000/users/me/configuration/" \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "lossPercent": 2.0,
    "profitPercent": 1.5,
    "quantityPerOrder": 100.0
  }'
```

## Security Notes

1. Always use HTTPS in production
2. Store API keys securely
3. Use strong passwords
4. Keep your `.env` file secure and never commit it to version control 
