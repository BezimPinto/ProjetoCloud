from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    @staticmethod
    def get_user(db: Session, user_id: int):
        return db.query(models.User).filter(models.User.id == user_id).first()

    @staticmethod
    def get_user_by_login(db: Session, login: str):
        return db.query(models.User).filter(models.User.login == login).first()

    @staticmethod
    def create_user(db: Session, user: schemas.UserCreate):
        hashed_password = pwd_context.hash(user.password)
        db_user = models.User(
            login=user.login,
            password=hashed_password,
            binanceApiKey=user.binanceApiKey,
            binanceSecretKey=user.binanceSecretKey,
            saldoInicio=user.saldoInicio
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

class UserConfigurationRepository:
    @staticmethod
    def create_user_configuration(db: Session, config: schemas.UserConfigurationCreate, user_id: int):
        db_config = models.UserConfiguration(**config.dict(), id_usuario=user_id)
        db.add(db_config)
        db.commit()
        db.refresh(db_config)
        return db_config

    @staticmethod
    def get_user_configuration(db: Session, user_id: int):
        return db.query(models.UserConfiguration).filter(models.UserConfiguration.id_usuario == user_id).first()

class UserTrackingTickerRepository:
    @staticmethod
    def create_tracking_ticker(db: Session, ticker: schemas.UserTrackingTickerCreate, user_id: int):
        db_ticker = models.UserTrackingTicker(**ticker.dict(), id_usuario=user_id)
        db.add(db_ticker)
        db.commit()
        db.refresh(db_ticker)
        return db_ticker

    @staticmethod
    def get_user_tickers(db: Session, user_id: int):
        return db.query(models.UserTrackingTicker).filter(models.UserTrackingTicker.id_usuario == user_id).all()

    @staticmethod
    def delete_tracking_ticker(db: Session, ticker_id: int, user_id: int):
        db_ticker = db.query(models.UserTrackingTicker).filter(
            models.UserTrackingTicker.id == ticker_id,
            models.UserTrackingTicker.id_usuario == user_id
        ).first()
        if db_ticker:
            db.delete(db_ticker)
            db.commit()
            return True
        return False 