import telebot
import Backend
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

ID = 0
users_data = {}

bot = telebot.TeleBot('7754833119:AAEIUSMefzMu2fR88kptn4MxD2N7h4vY57c')

@bot.message_handler(commands=['start', 'hello '])  # кнопки у сообщения бота
def main(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(f'👑 Фильтр уведомлений', callback_data='filter', parse_mode='HTML')  # кнопка Включить уведомления

    markup.row(btn1)  # 1 ряд
    bot.send_message(message.chat.id,
                     f'Приветствую, {message.from_user.first_name}, я ✨ <b>OpenProject Bot</b>✨ , и я здесь для того, чтобы присылать тебе уведомления!',
                     parse_mode='HTML', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: callback.data == 'filter')
def filter(callback):
    if callback.data == 'filter':
        markup = types.InlineKeyboardMarkup()
        btn3 = types.InlineKeyboardButton(f'Все уведомления', callback_data='all', parse_mode='HTML')
        btn4 = types.InlineKeyboardButton(f'По типу', callback_data='type', parse_mode='HTML')
        btn5 = types.InlineKeyboardButton(f'По id', callback_data='id', parse_mode='HTML')
        btn6 = types.InlineKeyboardButton(f'🔙 Назад', callback_data='back', parse_mode='HTML')

        markup.row(btn3)
        markup.row(btn4, btn5)
        bot.send_message(callback.message.chat.id,
                         f'Выберите тип уведомлений:',
                         parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: callback.data == 'all')
def all(callback):
    if callback.data == 'all':
        chat_id = callback.message.chat.id
        users_data[callback.from_user.id] = {
            'chat_id': chat_id,
            'type_of_notification': callback.data
        }
        markup = types.InlineKeyboardMarkup()
        btn7 = types.InlineKeyboardButton(f'🔙 Назад', callback_data='filter', parse_mode='HTML')

        markup.row(btn7)
        bot.send_message(callback.message.chat.id,
                         f'Вам будут приходить все уведомления!',
                         parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: callback.data == 'type')
def type(callback):
    if callback.data == 'type':
        markup = types.InlineKeyboardMarkup()

        btn_type1 = types.InlineKeyboardButton(f'Task', callback_data='task', parse_mode='HTML')
        btn_type2 = types.InlineKeyboardButton(f'Milestone', callback_data='milestone', parse_mode='HTML')
        btn_type3 = types.InlineKeyboardButton(f'Phase', callback_data='phase', parse_mode='HTML')
        btn8 = types.InlineKeyboardButton(f'🔙 Назад', callback_data='filter', parse_mode='HTML')

        markup.row(btn_type1)
        markup.row(btn_type2)
        markup.row(btn_type3)
        markup.row(btn8)
        bot.send_message(callback.message.chat.id,
                         f'Выберите тип события, уведомления о котором вы хотите получать:',
                         parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: callback.data == 'task')
def task(callback):
    if callback.data == 'task':
        chat_id = callback.message.chat.id
        users_data[callback.from_user.id] = {
            'chat_id': chat_id,
            'type_of_notification': 'task'
        }

        markup = types.InlineKeyboardMarkup()
        btn11 = types.InlineKeyboardButton(f'🔙 Назад', callback_data='type', parse_mode='HTML')

        bot.send_message(callback.message.chat.id,
                         f'Вам будут приходить уведомления о типе "Task"',
                         parse_mode='HTML', reply_markup=markup)
        markup.row(btn11)


@bot.callback_query_handler(func=lambda callback: callback.data == 'milestone')
def milestone(callback):
    if callback.data == 'milestone':
        chat_id = callback.message.chat.id
        users_data[callback.from_user.id] = {
            'chat_id': chat_id,
            'type_of_notification': callback.data
        }

        markup = types.InlineKeyboardMarkup()
        btn12 = types.InlineKeyboardButton(f'🔙 Назад', callback_data='type', parse_mode='HTML')

        bot.send_message(callback.message.chat.id,
                         f'Вам будут приходить уведомления о типе "Milestone"',
                         parse_mode='HTML', reply_markup=markup)
        markup.row(btn12)


@bot.callback_query_handler(func=lambda callback: callback.data == 'phase')
def phase(callback):
    if callback.data == 'phase':
        chat_id = callback.message.chat.id
        users_data[callback.from_user.id] = {
            'chat_id': chat_id,
            'type_of_notification': callback.data
        }

        markup = types.InlineKeyboardMarkup()
        btn13 = types.InlineKeyboardButton(f'🔙 Назад', callback_data='type', parse_mode='HTML')

        bot.send_message(callback.message.chat.id,
                         f'Вам будут приходить уведомления о типе "Phase"',
                         parse_mode='HTML', reply_markup=markup)
        markup.row(btn13)

@bot.callback_query_handler(func=lambda callback: callback.data == 'id')
def id(callback):
    if callback.data == 'id':
        markup = types.InlineKeyboardMarkup()
        btn9 = types.InlineKeyboardButton(f'🔙 Назад', callback_data='filter', parse_mode='HTML')

        msg = bot.send_message(callback.message.chat.id,
                         f'Введите id уведомления, которое вы хотите вывести:',
                         parse_mode='HTML', reply_markup=markup)

        markup.row(btn9)
        def get_ID(callback):
            global ID
            ID = int(callback.text)


        bot.register_next_step_handler(msg, get_ID)


@bot.callback_query_handler(func=lambda callback: callback.data == 'back')
def back(callback):
    if callback.data == 'back':
        main(callback.message)

#периодическая проверка данных и вывод уведомлений

def periodic_check():
    while True:
        print('543')
        for user_id, data in users_data.items():
            if data['type_of_notification'] == 'task':
                noti_arr = Backend.get_notifications_by_type(data['type_of_notification'])# Массив с тасками
                for n in noti_arr:
                    message_text = f'id: {n.id} event_type: {n.event_type} data: {json.loads(n.data)} created_at: {n.created_at}'
                    bot.send_message(data['chat_id'], message_text, parse_mode='HTML')
            elif data['type_of_notification'] == 'milestone':
                noti_arr = Backend.get_notifications_by_type(data['type_of_notification'])# Массив с майлами
                for n in noti_arr:
                    message_text = f'id: {n.id} event_type: {n.event_type} data: {json.loads(n.data)} created_at: {n.created_at}'
                    bot.send_message(data['chat_id'], message_text, parse_mode='HTML')
            elif data['type_of_notification'] == 'phase':
                noti_arr = Backend.get_notifications_by_type(data['type_of_notification'])# Массив с фазами
                for n in noti_arr:
                    message_text = f'id: {n.id} event_type: {n.event_type} data: {json.loads(n.data)} created_at: {n.created_at}'
                    bot.send_message(data['chat_id'], message_text, parse_mode='HTML')
            elif data['type_of_notification'] == 'all':
                noti_arr = Backend.get_notifications_by_type(data['type_of_notification'])
                for n in noti_arr:
                    message_text = f'id: {n.id} event_type: {n.event_type} data: {json.loads(n.data)} created_at: {n.created_at}'
                    bot.send_message(data['chat_id'], message_text, parse_mode='HTML')
            elif data['type_of_notification'] == 'id':
                n = Backend.get_notification_by_id(ID)
                message_text = f'id: {n.id} event_type: {n.event_type} data: {json.loads(n.data)} created_at: {n.created_at}'
                bot.send_message(data['chat_id'], message_text, parse_mode='HTML')
            else:
                pass

        time.sleep(5)  # Проверка каждые 60 секунд

if __name__ == 'main':
    # Запуск потока для периодической проверки базы данных
    thread = threading.Thread(target=periodic_check)
    thread.daemon = True #Завершение при выходе из программы
    thread.start()

bot.infinity_polling(none_stop=True)