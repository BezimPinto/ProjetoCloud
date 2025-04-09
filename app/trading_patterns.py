from typing import List
import pandas as pd
from binance.client import Client

class TradingPatterns:
    @staticmethod
    def is_engulfing(candles: List[dict]) -> bool:
        """
        Verifica se o último padrão de velas forma um padrão de engolfo
        """
        if len(candles) < 2:
            return False
            
        current = candles[-1]
        previous = candles[-2]
        
        # Verifica se é um engolfo de alta
        if (current['close'] > current['open'] and  # Vela atual é de alta
            previous['close'] < previous['open'] and  # Vela anterior é de baixa
            current['open'] < previous['close'] and  # Abertura atual menor que fechamento anterior
            current['close'] > previous['open']):    # Fechamento atual maior que abertura anterior
            return True
            
        # Verifica se é um engolfo de baixa
        if (current['close'] < current['open'] and  # Vela atual é de baixa
            previous['close'] > previous['open'] and  # Vela anterior é de alta
            current['open'] > previous['close'] and  # Abertura atual maior que fechamento anterior
            current['close'] < previous['open']):    # Fechamento atual menor que abertura anterior
            return True
            
        return False

    @staticmethod
    def is_inside_bar(candles: List[dict]) -> bool:
        """
        Verifica se o último padrão de velas forma um inside bar
        """
        if len(candles) < 2:
            return False
            
        current = candles[-1]
        previous = candles[-2]
        
        # Verifica se a vela atual está dentro da vela anterior
        return (current['high'] <= previous['high'] and
                current['low'] >= previous['low'])

class BinanceTrading:
    def __init__(self, api_key: str, api_secret: str):
        self.client = Client(api_key, api_secret)
        
    def get_klines(self, symbol: str, interval: str = Client.KLINE_INTERVAL_1HOUR, limit: int = 100) -> List[dict]:
        """
        Obtém os dados de candlesticks da Binance
        """
        klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
        return [{
            'open': float(k[1]),
            'high': float(k[2]),
            'low': float(k[3]),
            'close': float(k[4]),
            'volume': float(k[5])
        } for k in klines]
        
    def create_order(self, symbol: str, side: str, quantity: float, 
                    stop_price: float = None, take_profit_price: float = None):
        """
        Cria uma ordem com stop loss e take profit
        """
        # Primeiro cria a ordem principal
        order = self.client.create_order(
            symbol=symbol,
            side=side,
            type='MARKET',
            quantity=quantity
        )
        
        # Se especificado, cria ordem de stop loss
        if stop_price:
            self.client.create_order(
                symbol=symbol,
                side='SELL' if side == 'BUY' else 'BUY',
                type='STOP_LOSS_LIMIT',
                quantity=quantity,
                stopPrice=stop_price,
                price=stop_price
            )
            
        # Se especificado, cria ordem de take profit
        if take_profit_price:
            self.client.create_order(
                symbol=symbol,
                side='SELL' if side == 'BUY' else 'BUY',
                type='LIMIT',
                quantity=quantity,
                price=take_profit_price
            )
            
        return order 