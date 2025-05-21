import os
import logging
from telegram.ext import Application
from telegram.error import TelegramError
from dotenv import load_dotenv

class TelegramNotifier:
    def __init__(self):
        load_dotenv()
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.bot = None
        self.initialize()

    def initialize(self):
        """Initialize Telegram bot"""
        try:
            if not self.bot_token or not self.chat_id:
                logging.error("Telegram bot token or chat ID not found in environment variables")
                return False
            
            self.bot = Application.builder().token(self.bot_token).build()
            logging.info("Telegram bot initialized successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize Telegram bot: {str(e)}")
            return False

    async def send_message(self, message):
        """Send message to Telegram group"""
        try:
            if not self.bot:
                logging.error("Telegram bot not initialized")
                return False
            
            await self.bot.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            logging.info("Message sent to Telegram successfully")
            return True
        except TelegramError as e:
            logging.error(f"Failed to send Telegram message: {str(e)}")
            return False

    async def send_trade_notification(self, action, symbol, volume, price, sl=None, tp=None):
        """Send trade notification to Telegram group"""
        message = (
            f"🔔 <b>Trade {action}</b>\n\n"
            f"Symbol: {symbol}\n"
            f"Volume: {volume}\n"
            f"Price: {price}\n"
        )
        
        if sl:
            message += f"Stop Loss: {sl}\n"
        if tp:
            message += f"Take Profit: {tp}\n"
        
        return await self.send_message(message)

    async def send_error_notification(self, error_message):
        """Send error notification to Telegram group"""
        message = f"⚠️ <b>Error Alert</b>\n\n{error_message}"
        return await self.send_message(message)

    async def send_account_update(self, balance, equity, profit):
        """Send account update to Telegram group"""
        message = (
            f"📊 <b>Account Update</b>\n\n"
            f"Balance: {balance}\n"
            f"Equity: {equity}\n"
            f"Profit: {profit}\n"
        )
        return await self.send_message(message) 