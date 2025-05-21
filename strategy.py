import pandas as pd
import numpy as np
import ta
import logging

class TradingStrategy:
    def __init__(self, short_window=20, long_window=50):
        self.short_window = short_window
        self.long_window = long_window
        self.logger = logging.getLogger(__name__)

    def calculate_indicators(self, df):
        """Calculate technical indicators"""
        try:
            # Calculate moving averages
            df['SMA_short'] = ta.trend.sma_indicator(df['close'], window=self.short_window)
            df['SMA_long'] = ta.trend.sma_indicator(df['close'], window=self.long_window)
            
            # Calculate RSI
            df['RSI'] = ta.momentum.rsi(df['close'], window=14)
            
            # Calculate MACD
            macd = ta.trend.MACD(df['close'])
            df['MACD'] = macd.macd()
            df['MACD_signal'] = macd.macd_signal()
            
            return df
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {str(e)}")
            return None

    def generate_signals(self, df):
        """Generate trading signals based on strategy"""
        try:
            if df is None or len(df) < self.long_window:
                return None

            signals = pd.DataFrame(index=df.index)
            signals['signal'] = 0.0

            # Generate signals based on moving average crossover
            signals['signal'] = np.where(
                df['SMA_short'] > df['SMA_long'], 1.0, 0.0
            )

            # Generate trading orders
            signals['position'] = signals['signal'].diff()

            # Add RSI filter
            signals.loc[df['RSI'] > 70, 'position'] = 0  # Overbought
            signals.loc[df['RSI'] < 30, 'position'] = 0  # Oversold

            # Add MACD confirmation
            signals.loc[df['MACD'] < df['MACD_signal'], 'position'] = 0

            return signals
        except Exception as e:
            self.logger.error(f"Error generating signals: {str(e)}")
            return None

    def get_latest_signal(self, df):
        """Get the latest trading signal"""
        try:
            df_with_indicators = self.calculate_indicators(df)
            if df_with_indicators is None:
                return None

            signals = self.generate_signals(df_with_indicators)
            if signals is None or len(signals) == 0:
                return None

            latest_signal = signals['position'].iloc[-1]
            
            if latest_signal > 0:
                return "BUY"
            elif latest_signal < 0:
                return "SELL"
            else:
                return "HOLD"
        except Exception as e:
            self.logger.error(f"Error getting latest signal: {str(e)}")
            return None

    def should_close_position(self, df, position_type):
        """Determine if a position should be closed"""
        try:
            df_with_indicators = self.calculate_indicators(df)
            if df_with_indicators is None:
                return False

            latest_rsi = df_with_indicators['RSI'].iloc[-1]
            latest_macd = df_with_indicators['MACD'].iloc[-1]
            latest_macd_signal = df_with_indicators['MACD_signal'].iloc[-1]

            # Close long positions
            if position_type == "BUY":
                if latest_rsi > 70 or latest_macd < latest_macd_signal:
                    return True

            # Close short positions
            elif position_type == "SELL":
                if latest_rsi < 30 or latest_macd > latest_macd_signal:
                    return True

            return False
        except Exception as e:
            self.logger.error(f"Error checking position close: {str(e)}")
            return False 