from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserConfigurationBase(BaseModel):
    lossPercent: float
    profitPercent: float
    quantityPerOrder: float

class UserConfigurationCreate(UserConfigurationBase):
    pass

class UserConfiguration(UserConfigurationBase):
    id: int
    id_usuario: int

    class Config:
        from_attributes = True

class UserTrackingTickerBase(BaseModel):
    symbol: str

class UserTrackingTickerCreate(UserTrackingTickerBase):
    pass

class UserTrackingTicker(UserTrackingTickerBase):
    id: int
    id_usuario: int

    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    symbol: str
    side: str
    quantity: float
    price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    timestamp: datetime
    id_usuario: int
    is_completed: bool
    profit_loss: Optional[float] = None

    class Config:
        from_attributes = True

class PerformanceReportBase(BaseModel):
    start_date: datetime
    end_date: datetime
    total_profit_loss: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float

class PerformanceReportCreate(PerformanceReportBase):
    pass

class PerformanceReport(PerformanceReportBase):
    id: int
    id_usuario: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    login: str
    binanceApiKey: str
    binanceSecretKey: str
    saldoInicio: Optional[float] = None

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    configurations: List[UserConfiguration] = []
    tracking_tickers: List[UserTrackingTicker] = []
    transactions: List[Transaction] = []
    reports: List[PerformanceReport] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 