from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import os
from bot import bot

app = Flask(__name__)

# Setting up the database (PostgreSQL for Render)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./notifications.db")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
users = {}
def load_users_data():
    global users
    if os.path.exists('users_data.json'):
        try:
            with open('users_data.json', 'r') as f:
                users = json.load(f)
        except Exception:
            # Если файл пустой или некорректен, оставляем пустой словарь
            users = {}
load_users_data()

def save_users_data():
    with open('users_data.json', 'w') as f:
        json.dump(users, f)

# Defining the model to store notifications
class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)
    data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create the notifications table
Base.metadata.create_all(bind=engine)

# Function to save notification to the database
def save_notification(event_type, data):
    session = SessionLocal()
    notification = Notification(event_type=event_type, data=json.dumps(data))
    session.add(notification)
    session.commit()
    session.close()



# Main webhook handler
@app.route("/webhook", methods=["POST"])
def webhook_listener():
    try:
        # Получаем данные из запроса
        data = request.get_json()
        event_type = data.get("action", "unknown_event")

        # Сохраняем данные в базе данных
        save_notification(event_type, data)

        # Формируем текст сообщения без дополнительного преобразования JSON
        message_text = f'Получено уведомление. Событие: {event_type}. Информация: {json.dumps(data)}'
        print(message_text)
        bot.send_message(6881642446, message_text)
        # Отправляем сообщение пользователям
        for user_id, data in users.items():
            chat_id = data.get("chat_id")
            print(chat_id)
            bot.send_message(chat_id, message_text, parse_mode='HTML')

        return jsonify({"status": "success", "message": "Notification saved"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Functions to interact with notifications in the database

# Get all notifications
def get_all_notifications():
    session = SessionLocal()
    notifications = session.query(Notification).all()
    session.close()
    return [
        {"id": n.id, "event_type": n.event_type, "data": json.loads(n.data), "created_at": n.created_at}
        for n in notifications
    ]

# Get notifications by event type
def get_notifications_by_type(event_type):
    session = SessionLocal()
    notifications = session.query(Notification).filter(Notification.event_type == event_type).all()
    session.close()
    return [
        {"id": n.id, "event_type": n.event_type, "data": json.loads(n.data), "created_at": n.created_at}
        for n in notifications
    ]

# Get notification by ID
def get_notification_by_id(notification_id):
    session = SessionLocal()
    notification = session.query(Notification).filter(Notification.id == notification_id).first()
    session.close()
    if notification:
        return {
            "id": notification.id,
            "event_type": notification.event_type,
            "data": json.loads(notification.data),
            "created_at": notification.created_at
        }
    return None

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
