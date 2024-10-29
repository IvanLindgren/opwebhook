# Импортируем необходимые библиотеки
import telebot
import os
import json
from telebot import types
from bot import bot
# Глобальные переменные
ID = 0
users_data = {}  # Словарь для хранения данных пользователей

# Функции для работы с файлом users.json
def load_users_data():
    """Загрузка данных пользователей из файла users.json"""
    global users_data
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            users_data = json.load(f)
            print(json.load(f))
    else:
        users_data = {}

def save_users_data():
    """Сохранение данных пользователей в файл users.json"""
    with open('users.json', 'w') as f:
        json.dump(users_data, f)

# Инициализируем данные пользователей при запуске
load_users_data()

# Обработчик команд /start и /hello
@bot.message_handler(commands=['start', 'hello'])
def main(message):
    bot.send_message(
        message.chat.id,
        f'Приветствую! Я ✨ <b>OpenProject Bot</b>✨, и я здесь для того, чтобы присылать тебе уведомления!',
        parse_mode='HTML'
    )
    settings(message)

def settings(message):
    """Настройки уведомлений"""
    markup = types.InlineKeyboardMarkup()
    btn_stop = types.InlineKeyboardButton('🚫 Выключить уведомления', callback_data='stop')
    btn_not = types.InlineKeyboardButton('✅ Включить уведомления', callback_data='all')
    markup.row(btn_not)
    markup.row(btn_stop)
    bot.send_message(message.chat.id, '⚙️ Настройка уведомлений', parse_mode='HTML', reply_markup=markup)

# Обработчик для callback 'all' (включить уведомления)
@bot.callback_query_handler(func=lambda callback: callback.data == 'all')
def all(callback):
    chat_id = callback.message.chat.id
    users_data[callback.from_user.id] = {
        'chat_id': chat_id,
        'type_of_notification': callback.data
    }
    save_users_data()  # Сохраняем данные пользователя при подписке

    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton('🔙 Назад', callback_data='back')
    markup.row(btn_back)
    bot.send_message(
        callback.message.chat.id,
        '☑️ Вам будут приходить <b>все</b> уведомления!',
        parse_mode='HTML',
        reply_markup=markup
    )
    bot.answer_callback_query(callback.id, text='Вам будут приходить все уведомления!')
    bot.delete_message(callback.message.chat.id, callback.message.message_id)

# Обработчик для callback 'stop' (отключить уведомления)
@bot.callback_query_handler(func=lambda callback: callback.data == 'stop')
def stop(callback):
    chat_id = callback.message.chat.id
    if callback.from_user.id in users_data:
        del users_data[callback.from_user.id]  # Удаляем пользователя при отписке
        save_users_data()  # Сохраняем изменения в файл

    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton('🔙 Назад', callback_data='back')
    markup.row(btn_back)
    bot.send_message(
        callback.message.chat.id,
        'Вам больше не будут присылаться уведомления!',
        parse_mode='HTML',
        reply_markup=markup
    )
    bot.answer_callback_query(callback.id, text='Вам больше не будут приходить уведомления!')
    bot.delete_message(callback.message.chat.id, callback.message.message_id)

# Обработчик для callback 'back'
@bot.callback_query_handler(func=lambda callback: callback.data == 'back')
def back(callback):
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    settings(callback.message)

# Бесконечная обработка сообщений бота
bot.infinity_polling(none_stop=True)
