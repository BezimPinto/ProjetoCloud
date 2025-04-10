from binance.client import Client
from binance.exceptions import BinanceAPIException
import time

class BinanceTrading:
    def __init__(self, api_key: str, api_secret: str):
        self.client = Client(api_key, api_secret, {"recvWindow": 60000})  # Aumentando o recvWindow para 60 segundos
        self.server_time_offset = 0
        self._sync_time()

    def _sync_time(self):
        """Sincroniza o horário local com o servidor da Binance"""
        try:
            server_time = self.client.get_server_time()
            local_time = int(time.time() * 1000)
            self.server_time_offset = server_time['serverTime'] - local_time
            print(f"Server time offset: {self.server_time_offset}ms")
        except Exception as e:
            print(f"Error syncing time: {str(e)}")
            self.server_time_offset = 0

    def _get_current_timestamp(self):
        """Retorna o timestamp atual ajustado com o offset do servidor"""
        return int(time.time() * 1000) + self.server_time_offset

    def create_order(self, symbol: str, side: str, quantity: float, stop_price: float = None, take_profit_price: float = None):
        try:
            # Usa o timestamp ajustado
            timestamp = self._get_current_timestamp()

            # Cria a ordem de mercado
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity,
                timestamp=timestamp
            )

            # Se houver stop loss, cria a ordem de stop loss
            if stop_price:
                timestamp = self._get_current_timestamp()
                self.client.create_order(
                    symbol=symbol,
                    side='SELL' if side == 'BUY' else 'BUY',
                    type='STOP_LOSS_LIMIT',
                    timeInForce='GTC',
                    quantity=quantity,
                    stopPrice=stop_price,
                    price=stop_price,
                    timestamp=timestamp
                )

            # Se houver take profit, cria a ordem de take profit
            if take_profit_price:
                timestamp = self._get_current_timestamp()
                self.client.create_order(
                    symbol=symbol,
                    side='SELL' if side == 'BUY' else 'BUY',
                    type='TAKE_PROFIT_LIMIT',
                    timeInForce='GTC',
                    quantity=quantity,
                    stopPrice=take_profit_price,
                    price=take_profit_price,
                    timestamp=timestamp
                )

            return order
        except BinanceAPIException as e:
            if e.code == -1021:  # Erro de timestamp
                self._sync_time()  # Tenta sincronizar novamente
                timestamp = self._get_current_timestamp()
                # Tenta a ordem novamente com o novo timestamp
                return self.create_order(symbol, side, quantity, stop_price, take_profit_price)
            raise Exception(f"Binance API Error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error creating order: {str(e)}") 