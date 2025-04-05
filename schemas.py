from pydantic import BaseModel
from typing import Optional, List

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

class UserBase(BaseModel):
    login: str
    binanceApiKey: str
    binanceSecretKey: str
    saldoInicio: Optional[float] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    configurations: List[UserConfiguration] = []
    tracking_tickers: List[UserTrackingTicker] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 