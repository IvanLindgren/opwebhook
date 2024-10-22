# Импортируем необходимые библиотеки
import telebot
import Backend
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import os
import asyncio

# Инициализация приложения Flask
app = Flask(__name__)

# Настройка базы данных PostgreSQL для Render
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./notifications.db")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Определение модели для хранения уведомлений
class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)
    data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Создание таблицы уведомлений
Base.metadata.create_all(bind=engine)

# Функция для сохранения уведомления в базе данных
def save_notification(event_type, data):
    session = SessionLocal()
    notification = Notification(event_type=event_type, data=json.dumps(data))
    session.add(notification)
    session.commit()
    session.close()

# Основной обработчик вебхуков
@app.route("/webhook", methods=["POST"])
def webhook_listener():
    try:
        # Получение данных из запроса
        data = request.get_json()
        event_type = data.get("action", "unknown_event")

        # Сохранение данных в базу
        save_notification(event_type, data)

        return jsonify({"status": "success", "message": "Notification saved"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Инициализация бота
bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"), skip_pending=True)

# Глобальные переменные
users_data = {}

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
@bot.message_handler(commands=['start', 'hello'])
def main(message):
    # Создаем виртуальную клавиатуру
    markup = telebot.types.InlineKeyboardMarkup()

    # Добавляем кнопки в виртуальную клавиатуру
    btn1 = telebot.types.InlineKeyboardButton(f'👑 Фильтр уведомлений', callback_data='filter')
    btn_stop = telebot.types.InlineKeyboardButton(f'🚫 Выключить уведомления', callback_data='stop')

    # Добавляем строки в виртуальную клавиатуру
    markup.row(btn1)
    markup.row(btn_stop)

    # Отправляем начальное сообщение с виртуальной клавиатурой
    bot.send_message(message.chat.id,
                     f'Приветствую! Я ✨ <b>OpenProject Bot</b>✨, и я здесь для того, чтобы присылать тебе уведомления!',
                     parse_mode='HTML', reply_markup=markup)

# Асинхронная функция для отправки уведомления
async def send_notification(user_chat_id, message):
    await bot.send_message(user_chat_id, message, parse_mode='HTML')

# Асинхронная функция для обработки уведомлений
async def process_notifications():
    while True:
        for user_id, data in users_data.items():
            notifications = Backend.get_notifications_by_type(data['type_of_notification'])
            for notification in notifications:
                message_text = f"id: {notification['id']} event_type: {notification['event_type']} data: {notification['data']} created_at: {notification['created_at']}"
                await send_notification(data['chat_id'], message_text)

        await asyncio.sleep(10)

# Обработчик для callback 'begin'
@bot.callback_query_handler(func=lambda callback: callback.data == 'begin')
def begin(callback):
    if callback.data == 'begin':
        chat_id = callback.message.chat.id
        users_data[callback.from_user.id] = {
            'chat_id': chat_id,
            'type_of_notification': 'all'
        }
        save_users_data()
        bot.send_message(callback.message.chat.id,
                         f'☑️ По умолчанию вам будут приходить <b>все</b> уведомления!',
                         parse_mode='HTML')
        main(callback.message)

# Обработчик для callback 'filter'
@bot.callback_query_handler(func=lambda callback: callback.data == 'filter')
def filter(callback):
    if callback.data == 'filter':
        bot.clear_step_handler_by_chat_id(chat_id=callback.message.chat.id)
        markup = telebot.types.InlineKeyboardMarkup()
        btn3 = telebot.types.InlineKeyboardButton(f'🔔 Все уведомления', callback_data='all')
        btn4 = telebot.types.InlineKeyboardButton(f'🗂 По типу', callback_data='type')
        btn5 = telebot.types.InlineKeyboardButton(f'🔑 По id', callback_data='id')
        btn6 = telebot.types.InlineKeyboardButton(f'🔙 Назад', callback_data='back')

        markup.row(btn3)
        markup.row(btn4, btn5)
        markup.row(btn6)
        bot.send_message(callback.message.chat.id,
                         f'📣 Выберите тип уведомлений:',
                         parse_mode='HTML', reply_markup=markup)

# Обработчик для callback 'stop'
@bot.callback_query_handler(func=lambda callback: callback.data == 'stop')
def stop(callback):
    markup = telebot.types.InlineKeyboardMarkup()
    btn_begin = telebot.types.InlineKeyboardButton(f'✅ Включить уведомления', callback_data='begin')
    markup.row(btn_begin)

    bot.send_message(callback.message.chat.id,
                     f'Вам больше не будут присылаться уведомления!',
                     parse_mode='HTML', reply_markup=markup)

    chat_id = callback.message.chat.id
    users_data[callback.from_user.id] = {
        'chat_id': chat_id,
        'type_of_notification': callback.data
    }
    save_users_data()

# Обработчик для callback 'all'
@bot.callback_query_handler(func=lambda callback: callback.data == 'all')
def all(callback):
    if callback.data == 'all':
        chat_id = callback.message.chat.id
        users_data[callback.from_user.id] = {
            'chat_id': chat_id,
            'type_of_notification': callback.data
        }
        save_users_data()
        markup = telebot.types.InlineKeyboardMarkup()
        btn7 = telebot.types.InlineKeyboardButton(f'🔙 Назад', callback_data='filter')

        markup.row(btn7)
        bot.send_message(callback.message.chat.id,
                         f'☑️ Вам будут приходить <b>все</b> уведомления!',
                         parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(callback.id, text='Вам будут приходить все уведомления!')

if __name__ == "__main__":
    # Запуск асинхронной обработки уведомлений
    loop = asyncio.get_event_loop()
    loop.create_task(process_notifications())

    # Запуск бота
    bot.polling(none_stop=True)

    # Запуск Flask-сервера
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
