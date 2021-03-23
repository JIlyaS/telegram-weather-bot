import telebot
import os

token = os.environ["TELEGRAM_TOKEN"]

bot = telebot.TeleBot(token)
