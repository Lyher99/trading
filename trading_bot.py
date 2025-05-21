import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime
import time
import os
from dotenv import load_dotenv
import logging
import asyncio
from telegram_notifier import TelegramNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)

class ForexTradingBot:
    def __init__(self, symbol="XAUUSDm", timeframe=mt5.TIMEFRAME_M15):
        load_dotenv()
        self.symbol = symbol
        self.timeframe = timeframe
        self.initialized = False
        self.telegram = TelegramNotifier()
        self.max_positions = 3  # Maximum number of positions per direction
        self.grid_spacing = 0.2  # Grid spacing in percentage
        self.take_profit = 0.3  # Take profit in percentage
        self.stop_loss = 0.5    # Stop loss in percentage
        self.initialize_mt5()

    def initialize_mt5(self):
        """Initialize connection to MT5"""
        if not mt5.initialize():
            error_msg = "MT5 initialization failed"
            logging.error(error_msg)
            asyncio.run(self.telegram.send_error_notification(error_msg))
            return False
        
        # Check if the symbol exists
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            error_msg = f"Symbol {self.symbol} not found in Market Watch"
            logging.error(error_msg)
            asyncio.run(self.telegram.send_error_notification(error_msg))
            return False

        # If the symbol is not visible in MarketWatch, add it
        if not symbol_info.visible:
            if not mt5.symbol_select(self.symbol, True):
                error_msg = f"Failed to select {self.symbol}"
                logging.error(error_msg)
                asyncio.run(self.telegram.send_error_notification(error_msg))
                return False
        
        self.initialized = True
        logging.info("MT5 initialized successfully")
        asyncio.run(self.telegram.send_message("🤖 Trading bot initialized successfully"))
        return True

    def get_account_info(self):
        """Get account information"""
        if not self.initialized:
            return None
        return mt5.account_info()

    def get_market_data(self, num_candles=100):
        """Fetch recent market data"""
        if not self.initialized:
            return None
        
        try:
            # First check if we can get the current tick
            tick = mt5.symbol_info_tick(self.symbol)
            if tick is None:
                error_msg = f"Failed to get current tick for {self.symbol}"
                logging.error(error_msg)
                asyncio.run(self.telegram.send_error_notification(error_msg))
                return None

            # Then try to get the historical data
            rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, num_candles)
            if rates is None:
                error_msg = f"Failed to get market data for {self.symbol}"
                logging.error(error_msg)
                asyncio.run(self.telegram.send_error_notification(error_msg))
                return None
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Log the latest price
            latest_price = df['close'].iloc[-1]
            logging.info(f"Latest price for {self.symbol}: {latest_price}")
            
            return df
        except Exception as e:
            error_msg = f"Error getting market data: {str(e)}"
            logging.error(error_msg)
            asyncio.run(self.telegram.send_error_notification(error_msg))
            return None

    def place_order(self, order_type, volume, price=None, sl=None, tp=None):
        """Place a market order"""
        if not self.initialized:
            logging.error("MT5 not initialized")
            return None

        try:
            # Get symbol info
            symbol_info = mt5.symbol_info(self.symbol)
            if symbol_info is None:
                logging.error(f"Failed to get symbol info for {self.symbol}")
                return None

            # Check if symbol is available for trading
            if not symbol_info.visible:
                if not mt5.symbol_select(self.symbol, True):
                    logging.error(f"Failed to select {self.symbol}")
                    return None

            # Get current price if not provided
            if price is None:
                tick = mt5.symbol_info_tick(self.symbol)
                if tick is None:
                    logging.error(f"Failed to get current price for {self.symbol}")
                    return None
                price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid

            # Prepare the trade request
            point = symbol_info.point
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": volume,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 20,
                "magic": 234000,
                "comment": "python script order",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            # Log the request details
            logging.info(f"Placing order: {request}")

            # Send the order
            result = mt5.order_send(request)
            if result is None:
                logging.error("Order send failed - result is None")
                return None

            # Check the result
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = f"Order failed: {result.comment} (retcode: {result.retcode})"
                logging.error(error_msg)
                asyncio.run(self.telegram.send_error_notification(error_msg))
                return None
            
            # Log successful order
            action = "BUY" if order_type == mt5.ORDER_TYPE_BUY else "SELL"
            success_msg = f"Order placed successfully: {action} {volume} {self.symbol} at {price}"
            logging.info(success_msg)
            
            # Send notification
            asyncio.run(self.telegram.send_trade_notification(
                action=action,
                symbol=self.symbol,
                volume=volume,
                price=price,
                sl=sl,
                tp=tp
            ))
            
            return result

        except Exception as e:
            error_msg = f"Error placing order: {str(e)}"
            logging.error(error_msg)
            asyncio.run(self.telegram.send_error_notification(error_msg))
            return None

    def close_position(self, position_id):
        """Close a specific position"""
        if not self.initialized:
            return None

        try:
            position = mt5.positions_get(ticket=position_id)
            if position is None:
                error_msg = f"Position {position_id} not found"
                logging.error(error_msg)
                asyncio.run(self.telegram.send_error_notification(error_msg))
                return None

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position[0].symbol,
                "volume": position[0].volume,
                "type": mt5.ORDER_TYPE_SELL if position[0].type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "position": position_id,
                "price": mt5.symbol_info_tick(position[0].symbol).bid,
                "deviation": 20,
                "magic": 234000,
                "comment": "python script close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = f"Close position failed: {result.comment}"
                logging.error(error_msg)
                asyncio.run(self.telegram.send_error_notification(error_msg))
                return None
            
            asyncio.run(self.telegram.send_trade_notification(
                action="CLOSE",
                symbol=position[0].symbol,
                volume=position[0].volume,
                price=mt5.symbol_info_tick(position[0].symbol).bid
            ))
            
            logging.info(f"Position closed successfully: {result.comment}")
            return result
        except Exception as e:
            error_msg = f"Error closing position: {str(e)}"
            logging.error(error_msg)
            asyncio.run(self.telegram.send_error_notification(error_msg))
            return None

    def get_open_positions(self):
        """Get all open positions"""
        if not self.initialized:
            return None
        return mt5.positions_get()

    def send_account_update(self):
        """Send account update to Telegram"""
        account_info = self.get_account_info()
        if account_info:
            asyncio.run(self.telegram.send_account_update(
                balance=account_info.balance,
                equity=account_info.equity,
                profit=account_info.profit
            ))

    def shutdown(self):
        """Shutdown MT5 connection"""
        if self.initialized:
            mt5.shutdown()
            self.initialized = False
            asyncio.run(self.telegram.send_message("🛑 Trading bot shutdown"))
            logging.info("MT5 connection closed")

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

async def main():
    # Initialize the bot
    bot = ForexTradingBot()
    
    try:
        # Get account info
        account_info = bot.get_account_info()
        if account_info:
            logging.info(f"Balance: {account_info.balance}")
            logging.info(f"Equity: {account_info.equity}")
            bot.send_account_update()

        # Get symbol info for volume validation
        symbol_info = mt5.symbol_info(bot.symbol)
        if symbol_info is None:
            logging.error(f"Failed to get symbol info for {bot.symbol}")
            return

        # Main trading loop
        while True:
            try:
                # Get market data
                market_data = bot.get_market_data()
                if market_data is not None:
                    # Calculate indicators
                    market_data['SMA20'] = market_data['close'].rolling(window=20).mean()
                    market_data['SMA50'] = market_data['close'].rolling(window=50).mean()
                    market_data['RSI'] = calculate_rsi(market_data['close'], 14)
                    
                    # Get the latest values
                    current_price = market_data['close'].iloc[-1]
                    sma20 = market_data['SMA20'].iloc[-1]
                    sma50 = market_data['SMA50'].iloc[-1]
                    rsi = market_data['RSI'].iloc[-1]
                    
                    # Get current positions
                    positions = bot.get_open_positions()
                    buy_positions = []
                    sell_positions = []
                    
                    if positions:
                        for pos in positions:
                            if pos.symbol == bot.symbol:
                                if pos.type == mt5.ORDER_TYPE_BUY:
                                    buy_positions.append(pos)
                                else:
                                    sell_positions.append(pos)
                    
                    # Calculate base volume (0.1% of balance)
                    balance = account_info.balance
                    risk_amount = balance * 0.001
                    base_volume = round(risk_amount / current_price, 2)
                    
                    # Ensure volume meets minimum requirements
                    volume = max(base_volume, symbol_info.volume_min)
                    # Ensure volume doesn't exceed maximum
                    volume = min(volume, symbol_info.volume_max)
                    # Round to symbol's volume step
                    volume = round(volume / symbol_info.volume_step) * symbol_info.volume_step
                    
                    logging.info(f"Calculated volume: {volume} (min: {symbol_info.volume_min}, max: {symbol_info.volume_max}, step: {symbol_info.volume_step})")
                    
                    # Trading logic
                    # Check for buy opportunities
                    if len(buy_positions) < bot.max_positions:
                        if (sma20 > sma50 and rsi < 70) or (rsi < 30):  # Oversold or uptrend
                            # Place buy order
                            result = bot.place_order(
                                order_type=mt5.ORDER_TYPE_BUY,
                                volume=volume,
                                price=current_price,
                                sl=current_price * (1 - bot.stop_loss/100),
                                tp=current_price * (1 + bot.take_profit/100)
                            )
                            if result:
                                logging.info(f"Placed BUY order at {current_price} with volume {volume}")
                    
                    # Check for sell opportunities
                    if len(sell_positions) < bot.max_positions:
                        if (sma20 < sma50 and rsi > 30) or (rsi > 70):  # Overbought or downtrend
                            # Place sell order
                            result = bot.place_order(
                                order_type=mt5.ORDER_TYPE_SELL,
                                volume=volume,
                                price=current_price,
                                sl=current_price * (1 + bot.stop_loss/100),
                                tp=current_price * (1 - bot.take_profit/100)
                            )
                            if result:
                                logging.info(f"Placed SELL order at {current_price} with volume {volume}")
                    
                    # Check for take profit on existing positions
                    for pos in buy_positions + sell_positions:
                        current_profit = pos.profit
                        if current_profit > 0 and current_profit >= pos.volume * current_price * (bot.take_profit/100):
                            bot.close_position(pos.ticket)
                            logging.info(f"Closed position {pos.ticket} with profit {current_profit}")
                    
                    # Wait for 1 minute before next check
                    await asyncio.sleep(60)
                    
            except Exception as e:
                error_msg = f"Error in trading loop: {str(e)}"
                logging.error(error_msg)
                await bot.telegram.send_error_notification(error_msg)
                await asyncio.sleep(60)  # Wait before retrying

    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        logging.error(error_msg)
        await bot.telegram.send_error_notification(error_msg)
    
    finally:
        bot.shutdown()

if __name__ == "__main__":
    asyncio.run(main()) 