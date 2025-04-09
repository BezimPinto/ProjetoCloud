from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from . import models, schemas
from passlib.context import CryptContext
from datetime import datetime, timedelta
from . import auth

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
        
        # Convertendo para o schema User
        return schemas.User(
            id=db_user.id,
            login=db_user.login,
            binanceApiKey=db_user.binanceApiKey,
            binanceSecretKey=db_user.binanceSecretKey,
            saldoInicio=db_user.saldoInicio,
            configurations=[],
            tracking_tickers=[],
            transactions=[],
            reports=[]
        )

    @staticmethod
    def authenticate_user(db: Session, login: str, password: str):
        user = UserRepository.get_user_by_login(db, login)
        if not user:
            return False
        if not auth.verify_password(password, user.hashed_password):
            return False
        return user

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

class TransactionRepository:
    @staticmethod
    def create_transaction(db: Session, transaction: schemas.TransactionCreate, user_id: int):
        db_transaction = models.Transaction(**transaction.dict(), id_usuario=user_id)
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction

    @staticmethod
    def get_user_transactions(db: Session, user_id: int, start_date: datetime = None, end_date: datetime = None):
        query = db.query(models.Transaction).filter(models.Transaction.id_usuario == user_id)
        
        if start_date:
            query = query.filter(models.Transaction.timestamp >= start_date)
        if end_date:
            query = query.filter(models.Transaction.timestamp <= end_date)
            
        return query.order_by(models.Transaction.timestamp.desc()).all()

    @staticmethod
    def update_transaction_profit(db: Session, transaction_id: int, profit_loss: float):
        transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
        if transaction:
            transaction.profit_loss = profit_loss
            transaction.is_completed = True
            db.commit()
            return True
        return False

class PerformanceReportRepository:
    @staticmethod
    def create_report(db: Session, report: schemas.PerformanceReportCreate, user_id: int):
        db_report = models.PerformanceReport(**report.dict(), id_usuario=user_id)
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        return db_report

    @staticmethod
    def get_user_reports(db: Session, user_id: int, limit: int = 10):
        return db.query(models.PerformanceReport)\
            .filter(models.PerformanceReport.id_usuario == user_id)\
            .order_by(models.PerformanceReport.end_date.desc())\
            .limit(limit)\
            .all()

    @staticmethod
    def generate_report(db: Session, user_id: int, start_date: datetime, end_date: datetime):
        transactions = TransactionRepository.get_user_transactions(db, user_id, start_date, end_date)
        
        total_trades = len(transactions)
        winning_trades = sum(1 for t in transactions if t.profit_loss and t.profit_loss > 0)
        losing_trades = sum(1 for t in transactions if t.profit_loss and t.profit_loss < 0)
        total_profit_loss = sum(t.profit_loss or 0 for t in transactions)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        report = schemas.PerformanceReportCreate(
            start_date=start_date,
            end_date=end_date,
            total_profit_loss=total_profit_loss,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate
        )
        
        return PerformanceReportRepository.create_report(db, report, user_id) 