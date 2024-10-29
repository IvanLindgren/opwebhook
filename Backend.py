# backend.py
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from bot import bot  # импорт бота
from telebot import types
import os
import json
from sqlalchemy import BigInteger  # Импортируем BigInteger для поддержки больших значений



app = Flask(__name__)

# Настройка базы данных (например, PostgreSQL для Render)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./notifications.db")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Модель для уведомлений
class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)
    data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Модель для пользователей
# Модель для пользователей
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, unique=True, index=True)  # Изменено на String для хранения значений chat_id как строки
    type_of_notification = Column(String)


# Создание таблиц
Base.metadata.create_all(bind=engine)

# Функции для работы с пользователями в базе данных

def get_all_users():
    session = SessionLocal()
    users = session.query(User).all()
    print("Список пользователей:", users)  # Временно выводим список пользователей для проверки
    session.close()
    return users


def add_user(chat_id, type_of_notification):
    session = SessionLocal()
    user = session.query(User).filter(User.chat_id == chat_id).first()
    if user:
        user.type_of_notification = type_of_notification
    else:
        user = User(chat_id=chat_id, type_of_notification=type_of_notification)
        session.add(user)
    session.commit()
    session.close()

def remove_user(chat_id):
    session = SessionLocal()
    user = session.query(User).filter(User.chat_id == chat_id).first()
    if user:
        session.delete(user)
        session.commit()
    session.close()

def get_users():
    session = SessionLocal()
    users = session.query(User).all()
    session.close()
    return users

# Функция для сохранения уведомлений в базе данных
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
        # Получаем данные из запроса
        data = request.get_json()
        event_type = data.get("action", "unknown_event")

        # Сохраняем уведомление в базе данных
        save_notification(event_type, data)

        # Формируем текст сообщения
        message_text = f'Получено уведомление. Событие: {event_type}. Информация: {json.dumps(data)}'
        print(message_text)
        print(get_users())
        # Отправляем сообщение всем подписанным пользователям
        users = get_all_users()
        for user in users:
            chat_id = user.chat_id
            bot.send_message(chat_id, message_text, parse_mode='HTML')

        return jsonify({"status": "success", "message": "Notification saved"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    Base.metadata.drop_all(bind=engine)  # Удаляет все таблицы
    Base.metadata.create_all(bind=engine)  # Пересоздает таблицы с обновленным типом
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
