from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    binanceApiKey = Column(String(255), nullable=False)
    binanceSecretKey = Column(String(255), nullable=False)
    saldoInicio = Column(Float, nullable=True)

    configurations = relationship("UserConfiguration", back_populates="user")
    tracking_tickers = relationship("UserTrackingTicker", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    reports = relationship("PerformanceReport", back_populates="user")

class UserConfiguration(Base):
    __tablename__ = "user_configuration"

    id = Column(Integer, primary_key=True, index=True)
    lossPercent = Column(Float, nullable=False)
    profitPercent = Column(Float, nullable=False)
    quantityPerOrder = Column(Float, nullable=False)
    id_usuario = Column(Integer, ForeignKey('user.id'))

    user = relationship("User", back_populates="configurations")

class UserTrackingTicker(Base):
    __tablename__ = "user_tracking_ticker"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(255), nullable=False)
    id_usuario = Column(Integer, ForeignKey('user.id'))

    user = relationship("User", back_populates="tracking_tickers")

class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(255), nullable=False)
    side = Column(String(10), nullable=False)  # BUY or SELL
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    id_usuario = Column(Integer, ForeignKey('user.id'))
    is_completed = Column(Boolean, default=False)
    profit_loss = Column(Float, nullable=True)

    user = relationship("User", back_populates="transactions")

class PerformanceReport(Base):
    __tablename__ = "performance_report"

    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_profit_loss = Column(Float, nullable=False)
    total_trades = Column(Integer, nullable=False)
    winning_trades = Column(Integer, nullable=False)
    losing_trades = Column(Integer, nullable=False)
    win_rate = Column(Float, nullable=False)
    id_usuario = Column(Integer, ForeignKey('user.id'))

    user = relationship("User", back_populates="reports") 