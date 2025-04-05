from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from . import models, schemas, repository, auth, database
from .database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Binance Trading Bot API")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.login}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = repository.UserRepository.get_user_by_login(db, login=user.login)
    if db_user:
        raise HTTPException(status_code=400, detail="Login already registered")
    return repository.UserRepository.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(
    current_user: models.User = Depends(auth.get_current_user)
):
    return current_user

@app.post("/users/me/configuration/", response_model=schemas.UserConfiguration)
async def create_user_configuration(
    config: schemas.UserConfigurationCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return repository.UserConfigurationRepository.create_user_configuration(
        db=db, config=config, user_id=current_user.id
    )

@app.get("/users/me/configuration/", response_model=schemas.UserConfiguration)
async def get_user_configuration(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    config = repository.UserConfigurationRepository.get_user_configuration(db, current_user.id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config

@app.post("/users/me/tracking-tickers/", response_model=schemas.UserTrackingTicker)
async def create_tracking_ticker(
    ticker: schemas.UserTrackingTickerCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return repository.UserTrackingTickerRepository.create_tracking_ticker(
        db=db, ticker=ticker, user_id=current_user.id
    )

@app.get("/users/me/tracking-tickers/", response_model=List[schemas.UserTrackingTicker])
async def get_user_tracking_tickers(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return repository.UserTrackingTickerRepository.get_user_tickers(db, current_user.id)

@app.delete("/users/me/tracking-tickers/{ticker_id}")
async def delete_tracking_ticker(
    ticker_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    success = repository.UserTrackingTickerRepository.delete_tracking_ticker(
        db, ticker_id, current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Ticker not found")
    return {"status": "success"} 