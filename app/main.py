from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import List

from . import models, schemas, repository, database
from .database import engine
from .trading_patterns import TradingPatterns, BinanceTrading

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Binance Trading Bot API")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usuário padrão com suas chaves da Binance
DEFAULT_USER = {
    "id": 100,
    "login": "default_user",
    "binanceApiKey": "RfX5oncCDt1OVR4Ld1btOqKIzai9tqPTZtERnRhXbeDqLnT73ngluWf0TpNAuRhY",
    "binanceSecretKey": "TQKNXzHWVVXlA5yvn9qh3PoCqLkUjCkH0hTMS33tCfdt1hXBFPgEMOokqOlySUsP",
    "saldoInicio": 1000.0
}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print(user.login)
    try:
        db_user = repository.UserRepository.get_user_by_login(db, login=user.login)
        if db_user:
            raise HTTPException(status_code=400, detail="Login already registered")
        return repository.UserRepository.create_user(db=db, user=user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the user: {str(e)}"
        )
@app.delete("/users/{user_id}", response_model=dict)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = repository.UserRepository.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    repository.UserRepository.delete_user(db, user_id)
    return {"status": "success", "message": f"User with ID {user_id} deleted."}


@app.post("/users/{user_id}/configurations/", response_model=schemas.UserConfiguration)
async def create_user_configuration(
    user_id: int,
    config: schemas.UserConfigurationCreate,
    db: Session = Depends(get_db)
):
    # Verifica se o usuário existe
    user = repository.UserRepository.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return repository.UserConfigurationRepository.create_user_configuration(
        db=db, config=config, user_id=user_id
    )

@app.get("/users/{user_id}/configurations/", response_model=schemas.UserConfiguration)
async def get_user_configuration(
    user_id: int,
    db: Session = Depends(get_db)
):
    config = repository.UserConfigurationRepository.get_user_configuration(db, user_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config

@app.post("/users/{user_id}/tracking-tickers/", response_model=schemas.UserTrackingTicker)
async def create_tracking_ticker(
    user_id: int,
    ticker: schemas.UserTrackingTickerCreate,
    db: Session = Depends(get_db)
):
    # Verifica se o usuário existe
    user = repository.UserRepository.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return repository.UserTrackingTickerRepository.create_tracking_ticker(
        db=db, ticker=ticker, user_id=user_id
    )

@app.get("/users/{user_id}/tracking-tickers/", response_model=List[schemas.UserTrackingTicker])
async def get_user_tracking_tickers(
    user_id: int,
    db: Session = Depends(get_db)
):
    # Verifica se o usuário existe
    user = repository.UserRepository.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return repository.UserTrackingTickerRepository.get_user_tickers(db, user_id)

@app.delete("/users/{user_id}/tracking-tickers/{ticker_id}")
async def delete_tracking_ticker(
    user_id: int,
    ticker_id: int,
    db: Session = Depends(get_db)
):
    # Verifica se o usuário existe
    user = repository.UserRepository.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    success = repository.UserTrackingTickerRepository.delete_tracking_ticker(
        db, ticker_id, user_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Ticker not found")
    return {"status": "success"}

@app.post("/users/{user_id}/transactions/", response_model=schemas.Transaction)
async def create_transaction(
    user_id: int,
    transaction: schemas.TransactionRequest,
    db: Session = Depends(get_db)
):
    # Verifica se o usuário existe
    user = repository.UserRepository.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verifica se o usuário possui configurações definidas
    config = repository.UserConfigurationRepository.get_user_configuration(db, user_id)
    if not config:
        raise HTTPException(status_code=400, detail="User configuration not found")

    # Obtém o preço atual do ativo
    try:
        trading = BinanceTrading(user.binanceApiKey, user.binanceSecretKey)
        ticker = trading.client.get_symbol_ticker(symbol=transaction.symbol)
        current_price = float(ticker['price'])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error getting price: {str(e)}")

    # Calcula a quantidade com base no valor total e no preço atual
    quantity = transaction.valorTotal / current_price

    # Validação: se for SELL, não permitir vender mais do que a quantidade disponível
    if transaction.side.upper() == "SELL":
        # Recupera todas as transações já realizadas pelo usuário
        transactions = repository.TransactionRepository.get_user_transactions(db, user_id)
        # Calcula a posição líquida: soma das compras menos soma das vendas
        net_quantity = sum(
            t.quantity if t.side.upper() == "BUY" else -t.quantity
            for t in transactions
        )
        if quantity > net_quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Quantidade para SELL ({quantity:.4f}) excede a posição disponível ({net_quantity:.4f})."
            )

    # Cria a transação no banco de dados (com base em schemas.TransactionCreate)
    db_transaction = repository.TransactionRepository.create_transaction(
        db=db,
        transaction=schemas.TransactionCreate(
            symbol=transaction.symbol,
            side=transaction.side,
            valorTotal=transaction.valorTotal,
            price=current_price,
            stop_loss=None,
            take_profit=None
        ),
        user_id=user_id,
        quantity=quantity
    )

    # Executa a ordem na Binance com os parâmetros adequados
    try:
        # Calcula stop loss e take profit baseado na configuração do usuário
        if transaction.side.upper() == "BUY":
            stop_loss = current_price * (1 - config.lossPercent/100)
            take_profit = current_price * (1 + config.profitPercent/100)
        else:  # SELL
            stop_loss = current_price * (1 + config.lossPercent/100)
            take_profit = current_price * (1 - config.profitPercent/100)

        trading.create_order(
            symbol=transaction.symbol,
            side=transaction.side,
            quantity=quantity,
            stop_price=stop_loss,
            take_profit_price=take_profit
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return db_transaction


@app.get("/users/{user_id}/transactions/", response_model=List[schemas.TransactionResponse])
async def get_user_transactions(
    user_id: int,
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db)
):
    # Verifica se o usuário existe
    user = repository.UserRepository.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    transactions = repository.TransactionRepository.get_user_transactions(db, user_id, start_date, end_date)
    
    # Cria uma instância do cliente Binance usando as chaves do usuário para obter a cotação atual
    trading = BinanceTrading(user.binanceApiKey, user.binanceSecretKey)
    
    enriched_transactions = []
    for t in transactions:
        try:
            ticker = trading.client.get_symbol_ticker(symbol=t.symbol)
            current_price = float(ticker['price'])
        except Exception as e:
            current_price = 0.0
        # Calcula o valor atual de cada transação com base na quantidade negociada
        current_value = t.quantity * current_price
        # Define a moeda negociada; neste exemplo, usamos o símbolo completo
        traded_coin = t.symbol
        enriched_transaction = {**t.dict(), "current_value": current_value, "traded_coin": traded_coin}
        enriched_transactions.append(enriched_transaction)
    
    return enriched_transactions


@app.get("/users/{user_id}/net-quantity/")
async def get_net_quantity(user_id: int, db: Session = Depends(get_db)):
    # Verifica se o usuário existe
    user = repository.UserRepository.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Recupera todas as transações do usuário
    transactions = repository.TransactionRepository.get_user_transactions(db, user_id)
    
    net_quantity = 0.0
    # Para cada transação, se for BUY soma a quantidade, se for SELL subtrai a quantidade
    for t in transactions:
        if t.side.upper() == "BUY":
            net_quantity += t.quantity
        elif t.side.upper() == "SELL":
            net_quantity -= t.quantity
    
    return {
        "user_id": user_id,
        "net_quantity": net_quantity,
        "total_transactions": len(transactions)
    }


@app.get("/prices/{symbol}")
async def get_price(
    symbol: str
):
    try:
        trading = BinanceTrading(DEFAULT_USER["binanceApiKey"], DEFAULT_USER["binanceSecretKey"])
        ticker = trading.client.get_symbol_ticker(symbol=symbol)
        return {
            "symbol": symbol,
            "price": float(ticker['price']),
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/prices/klines/{symbol}")
async def get_klines(
    symbol: str,
    interval: str = "1h",
    limit: int = 100
):
    """
    Obtém dados históricos de preços (candlesticks) de um par de criptomoedas
                // ⏰ Timestamp de abertura (em milissegundos desde 1970)
                // 💵 Preço de abertura
                // 🔼 Preço máximo
                // 🔽 Preço mínimo
                // ✅ Preço de fechamento
                // 📊 Volume negociado
                // ⏰ Timestamp de fechamento
                // 💰 Volume negociado em USDT
                // 🔁 Número de trades
                // 🛒 Volume de compra
                // 🛍️ Volume de venda
                // ❓ Campo ignorado
    
    """
    try:
        trading = BinanceTrading(DEFAULT_USER["binanceApiKey"], DEFAULT_USER["binanceSecretKey"])
        klines = trading.client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit
        )
        return {
            "symbol": symbol,
            "interval": interval,
            "klines": klines
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
