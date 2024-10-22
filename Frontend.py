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

from bot import bot


# Функция для сохранения данных пользователей в файл .json
def save_users_data():
    with open('users_data.json', 'w') as f:
        json.dump(users_data, f)

# Функция для загрузки данных пользователей из файла .json
def load_users_data():
    global users_data
    if os.path.exists('users_data.json'):
        with open('users_data.json', 'r') as f:
            users_data = json.load(f)

# Загрузка данных пользователей при старте бота
load_users_data()


# Обработчик команд /start и /hello
@bot.message_handler(commands=['start', 'hello '])
def main(message):
    # Создаем виртуальную клавиатуру
    markup = types.InlineKeyboardMarkup()

    # Добавляем кнопки в виртуальную клавиатуру
    btn1 = types.InlineKeyboardButton(f'👑 Фильтр уведомлений', callback_data='filter', parse_mode='HTML')  # Кнопка включить уведомления
    btn_stop = types.InlineKeyboardButton(f'🚫 Выключить уведомления', callback_data='stop', parse_mode='HTML')

    # Добавляем строки в виртуальную клавиатуру
    markup.row(btn1)  # Первая строка
    markup.row(btn_stop)

    # Отправляем начальное сообщение с виртуальной клавиатурой
    bot.send_message(message.chat.id,
                     f'Приветствую! Я ✨ <b>OpenProject Bot</b>✨, и я здесь для того, чтобы присылать тебе уведомления!',
                     parse_mode='HTML', reply_markup=markup)

# Обработчик для callback 'begin'
@bot.callback_query_handler(func=lambda callback: callback.data == 'begin')
def begin(callback):
    if callback.data == 'begin':
        chat_id = callback.message.chat.id
        users_data[callback.from_user.id] = {
            'chat_id': chat_id,
            'type_of_notification': 'all'
        }
        with open("users_data.json", "w") as f:
            json.dump(users_data, f)
        bot.send_message(callback.message.chat.id,
                         f'☑️ По умолчанию вам будут приходить <b>все</b> уведомления!',
                         parse_mode='HTML')
        main(callback.message)

# Обработчик для callback 'filter'
@bot.callback_query_handler(func=lambda callback: callback.data == 'filter')
def filter(callback):
    if callback.data == 'filter':
        bot.clear_step_handler_by_chat_id(chat_id=callback.message.chat.id)
        markup = types.InlineKeyboardMarkup()
        btn3 = types.InlineKeyboardButton(f'🔔 Все уведомления', callback_data='all', parse_mode='HTML')
        btn4 = types.InlineKeyboardButton(f'🗂 По типу', callback_data='type', parse_mode='HTML')
        btn5 = types.InlineKeyboardButton(f'🔑 По id', callback_data='id', parse_mode='HTML')
        btn6 = types.InlineKeyboardButton(f'🔙 Назад', callback_data='back', parse_mode='HTML')

        markup.row(btn3)
        markup.row(btn4, btn5)
        markup.row(btn6)
        bot.send_message(callback.message.chat.id,
                         f'📣 Выберите тип уведомлений:',
                         parse_mode='HTML', reply_markup=markup)

# Обработчик для callback 'stop'
@bot.callback_query_handler(func=lambda callback: callback.data == 'stop')
def stop(callback):
    markup = types.InlineKeyboardMarkup()
    btn_begin = types.InlineKeyboardButton(f'✅ Включить уведомления', callback_data='begin', parse_mode='HTML')
    markup.row(btn_begin)

    bot.send_message(callback.message.chat.id,
                     f'Вам больше не будут присылаться уведомления!',
                     parse_mode='HTML', reply_markup=markup)

    chat_id = callback.message.chat.id
    users_data[callback.from_user.id] = {
        'chat_id': chat_id,
        'type_of_notification': callback.data
    }
    with open("users_data.json", "w") as f:
        json.dump(users_data, f)

# Обработчик для callback 'all'
@bot.callback_query_handler(func=lambda callback: callback.data == 'all')
def all(callback):
    if callback.data == 'all':
        chat_id = callback.message.chat.id
        users_data[callback.from_user.id] = {
            'chat_id': chat_id,
            'type_of_notification': callback.data
        }
        with open("users_data.json", "w") as f:
            json.dump(users_data, f)
        markup = types.InlineKeyboardMarkup()
        btn7 = types.InlineKeyboardButton(f'🔙 Назад', callback_data='filter', parse_mode='HTML')

        markup.row(btn7)
        bot.send_message(callback.message.chat.id,
                         f'☑️ Вам будут приходить <b>все</b> уведомления!',
                         parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(callback.id, text='Вам будут приходить все уведомления!')

# Обработчик для callback 'type'
@bot.callback_query_handler(func=lambda callback: callback.data == 'type')
def type(callback):
    if callback.data == 'type':
        markup = types.InlineKeyboardMarkup()

        btn_type1 = types.InlineKeyboardButton(f'🔸 Task', callback_data='task', parse_mode='HTML')
        btn_type2 = types.InlineKeyboardButton(f'🔹 Milestone', callback_data='milestone', parse_mode='HTML')
        btn_type3 = types.InlineKeyboardButton(f'🔸 Phase', callback_data='phase', parse_mode='HTML')
        btn8 = types.InlineKeyboardButton(f'🔙 Назад', callback_data='filter', parse_mode='HTML')

        markup.row(btn_type1)
        markup.row(btn_type2)
        markup.row(btn_type3)
        markup.row(btn8)
        bot.send_message(callback.message.chat.id,
                         f'🗞 Выберите тип события, уведомления о котором вы хотите получать:',
                         parse_mode='HTML', reply_markup=markup)

# Обработчик для callback 'task'
@bot.callback_query_handler(func=lambda callback: callback.data == 'task')
def task(callback):
    if callback.data == 'task':
        chat_id = callback.message.chat.id
        users_data[callback.from_user.id] = {
            'chat_id': chat_id,
            'type_of_notification': 'task'
        }
        with open("users_data.json", "w") as f:
            json.dump(users_data, f)
        markup = types.InlineKeyboardMarkup()
        btn11 = types.InlineKeyboardButton(f'🔙 Назад', callback_data='type', parse_mode='HTML')
        markup.row(btn11)

        bot.send_message(callback.message.chat.id,
                         f'☑️ Вам будут приходить уведомления типа "Task"',
                         parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(callback.id, text='Вам будут приходить уведомления типа <b>"Task"</b>')

# Обработчик для callback 'milestone'
@bot.callback_query_handler(func=lambda callback: callback.data == 'milestone')
def milestone(callback):
    if callback.data == 'milestone':
        chat_id = callback.message.chat.id
        users_data[callback.from_user.id] = {
            'chat_id': chat_id,
            'type_of_notification': callback.data
        }
        with open("users_data.json", "w") as f:
            json.dump(users_data, f)
        markup = types.InlineKeyboardMarkup()
        btn12 = types.InlineKeyboardButton(f'🔙 Назад', callback_data='type', parse_mode='HTML')
        markup.row(btn12)

        bot.send_message(callback.message.chat.id,
                         f'☑️ Вам будут приходить уведомления типа "Milestone"',
                         parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(callback.id, text='Вам будут приходить уведомления типа <b>"Milestone"</b>')

# Обработчик для callback 'phase'
@bot.callback_query_handler(func=lambda callback: callback.data == 'phase')
def phase(callback):
    if callback.data == 'phase':
        chat_id = callback.message.chat.id
        users_data[callback.from_user.id] = {
            'chat_id': chat_id,
            'type_of_notification': callback.data
        }
        with open("users_data.json", "w") as f:
            json.dump(users_data, f)
        markup = types.InlineKeyboardMarkup()
        btn13 = types.InlineKeyboardButton(f'🔙 Назад', callback_data='type', parse_mode='HTML')
        markup.row(btn13)

        bot.send_message(callback.message.chat.id,
                         f'☑️ Вам будут приходить уведомления типа "Phase"',
                         parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(callback.id, text='Вам будут приходить уведомления типа <b>"Phase"</b>')

# Обработчик для callback 'id'
@bot.callback_query_handler(func=lambda callback: callback.data == 'id')
def id(callback):
    if callback.data == 'id':
        markup = types.InlineKeyboardMarkup()
        btn9 = types.InlineKeyboardButton(f'🔙 Назад', callback_data='filter', parse_mode='HTML')
        markup.row(btn9)

        msg = bot.send_message(callback.message.chat.id,
                             f'📌 Введите id уведомления, которое вы хотите вывести:',
                             parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(callback.id, text="Пожалуйста, введите ID уведомления")

        bot.register_next_step_handler(msg, handle_input)

# Функция для обработки ввода ID
def get_ID(callback):
    global ID
    ID = int(callback.text)

# Обработчик для callback 'input'
@bot.callback_query_handler(func=lambda callback: callback.data == 'input')
def handle_input(message):
    if message.text.isdigit():
        get_ID(message)
        notification = Backend.get_notification_by_id(ID)

        if notification:
            markup = types.InlineKeyboardMarkup()
            btn_b = types.InlineKeyboardButton(f'🔙 Назад', callback_data='filter', parse_mode='HTML')
            markup.row(btn_b)
            message_text = f'id: {notification.id} event_type: {notification.event_type} data: {json.loads(notification.data)} created_at: {notification.created_at}'
            bot.send_message(message.from_user.id, message_text, parse_mode='HTML')

        else:
            markup = types.InlineKeyboardMarkup()
            btn_b = types.InlineKeyboardButton(f'🔙 Назад', callback_data='filter', parse_mode='HTML')
            markup.row(btn_b)

            bot.send_message(message.from_user.id, "❗️ Такого уведомления не найдено", parse_mode='HTML', reply_markup=markup)
            bot.register_next_step_handler(message, handle_input)

    else:
        markup = types.InlineKeyboardMarkup()
        btn_b = types.InlineKeyboardButton(f'🔙 Назад', callback_data='filter', parse_mode='HTML')
        markup.row(btn_b)

        bot.send_message(message.from_user.id, "Пожалуйста, введите корректный ID уведомления", reply_markup=markup)
        bot.register_next_step_handler(message, handle_input)

# Обработчик для callback 'back'
@bot.callback_query_handler(func=lambda callback: callback.data == 'back')
def back(callback):
    if callback.data == 'back':
        main(callback.message)

# Функция для периодической проверки данных и вывода уведомлений
def periodic_check():
    while True:
        for user_id, data in users_data.items():
            if data['type_of_notification'] == 'task':
                noti_arr = Backend.get_notifications_by_type(data['type_of_notification'])
                for n in noti_arr:
                    message_text = f'id: {n.id} event_type: {n.event_type} data: {json.loads(n.data)} created_at: {n.created_at}'
                    bot.send_message(data['chat_id'], message_text, parse_mode='HTML')

            elif data['type_of_notification'] == 'milestone':
                noti_arr = Backend.get_notifications_by_type(data['type_of_notification'])
                for n in noti_arr:
                    message_text = f'id: {n.id} event_type: {n.event_type} data: {json.loads(n.data)} created_at: {n.created_at}'
                    bot.send_message(data['chat_id'], message_text, parse_mode='HTML')

            elif data['type_of_notification'] == 'phase':
                noti_arr = Backend.get_notifications_by_type(data['type_of_notification'])
                for n in noti_arr:
                    message_text = f'id: {n.id} event_type: {n.event_type} data: {json.loads(n.data)} created_at: {n.created_at}'
                    bot.send_message(data['chat_id'], message_text, parse_mode='HTML')

            elif data['type_of_notification'] == 'all':
                noti_arr = Backend.get_notifications_by_type(data['type_of_notification'])
                for n in noti_arr:
                    message_text = f'id: {n.id} event_type: {n.event_type} data: {json.loads(n.data)} created_at: {n.created_at}'
                    bot.send_message(data['chat_id'], message_text, parse_mode='HTML')
            else:
                pass
        time.sleep(60)

if __name__ == '__main__':
    # Запуск потока для периодической проверки базы данных
    thread = threading.Thread(target=periodic_check)
    thread.daemon = True # Устанавливаем как демонный поток (завершается при выходе из программы)
    thread.start()

# Бесконечная обработка сообщений бота
bot.infinity_polling(none_stop=True)
