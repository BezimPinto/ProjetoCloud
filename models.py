from sqlalchemy import Column, Integer, String, Double, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    binanceApiKey = Column(String(255), nullable=False)
    binanceSecretKey = Column(String(255), nullable=False)
    saldoInicio = Column(Double, nullable=True)

    configurations = relationship("UserConfiguration", back_populates="user")
    tracking_tickers = relationship("UserTrackingTicker", back_populates="user")

class UserConfiguration(Base):
    __tablename__ = "user_configuration"

    id = Column(Integer, primary_key=True, index=True)
    lossPercent = Column(Double, nullable=False)
    profitPercent = Column(Double, nullable=False)
    quantityPerOrder = Column(Double, nullable=False)
    id_usuario = Column(Integer, ForeignKey('user.id'))

    user = relationship("User", back_populates="configurations")

class UserTrackingTicker(Base):
    __tablename__ = "user_tracking_ticker"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(255), nullable=False)
    id_usuario = Column(Integer, ForeignKey('user.id'))

    user = relationship("User", back_populates="tracking_tickers") 