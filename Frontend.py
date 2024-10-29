# Импортируем необходимые библиотеки
import telebot
import webbrowser
import sqlite3
import re
import Backend
from flask import *
import json
import os
from telebot import types, callback_data
import time
import threading

# Глобальные переменные
ID = 0
users_data = {}  # Словарь для хранения данных пользователей

# Инициализация бота
bot = telebot.TeleBot('7754833119:AAEIUSMefzMu2fR88kptn4MxD2N7h4vY57c', skip_pending=True)

# Обработчик команд /start и /hello
@bot.message_handler(commands=[])
def settings(message):
    markup = types.InlineKeyboardMarkup()
    btn_stop = types.InlineKeyboardButton(f'🚫 Выключить уведомления', callback_data='stop', parse_mode='HTML')
    btn_not = types.InlineKeyboardButton(f'✅ Включить уведомления', callback_data='all', parse_mode='HTML')

    markup.row(btn_not)
    markup.row(btn_stop)

    bot.send_message(message.chat.id,
                     f'⚙️ Настройка уведомлений',
                     parse_mode='HTML', reply_markup=markup)

@bot.message_handler(commands=['start', 'hello '])
def main(message):

    bot.send_message(message.chat.id,
                     f'Приветствую! Я ✨ <b>OpenProject Bot</b>✨, и я здесь для того, чтобы присылать тебе уведомления!',
                     parse_mode='HTML')
    settings(message)

# Обработчик для callback 'all'
@bot.callback_query_handler(func=lambda callback: callback.data == 'all')
def all(callback):
    if callback.data == 'all':
        chat_id = callback.message.chat.id
        users_data[callback.from_user.id] = {
            'chat_id': chat_id,
            'type_of_notification': callback.data
        }
        markup = types.InlineKeyboardMarkup()
        btn7 = types.InlineKeyboardButton(f'🔙 Назад', callback_data='back', parse_mode='HTML')

        markup.row(btn7)
        bot.send_message(callback.message.chat.id,
                         f'☑️ Вам будут приходить <b>все</b> уведомления!',
                         parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(callback.id, text='Вам будут приходить все уведомления!')
        bot.delete_message(callback.message.chat.id, callback.message.message_id)

# Обработчик для callback 'stop'
@bot.callback_query_handler(func=lambda callback: callback.data == 'stop')
def stop(callback):

    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(f'🔙 Назад', callback_data='back', parse_mode='HTML')
    markup.row(btn_back)

    bot.send_message(callback.message.chat.id,
                     f'Вам больше не будут присылаться уведомления!',
                     parse_mode='HTML', reply_markup=markup)
    bot.answer_callback_query(callback.id, text='Вам больше не будут приходить уведомления!')
    bot.delete_message(callback.message.chat.id, callback.message.message_id)

    chat_id = callback.message.chat.id
    users_data[callback.from_user.id] = {
        'chat_id': chat_id,
        'type_of_notification': callback.data
    }

# Обработчик для callback 'back'
@bot.callback_query_handler(func=lambda callback: callback.data == 'back')
def back(callback):
    if callback.data == 'back':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        settings(callback.message)

# Бесконечная обработка сообщений бота
bot.infinity_polling(none_stop=True)