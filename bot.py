# bot.py
from telebot import TeleBot
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = TeleBot(TOKEN, skip_pending=True)
