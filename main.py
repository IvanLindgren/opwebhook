from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

app = Flask(__name__)

# Настройка базы данных SQLite
DATABASE_URL = "sqlite:///./notifications.db"
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

# Функции для работы с уведомлениями в базе данных

# Получение всех уведомлений
def get_all_notifications():
    session = SessionLocal()
    notifications = session.query(Notification).all()
    session.close()
    return [
        {"id": n.id, "event_type": n.event_type, "data": json.loads(n.data), "created_at": n.created_at}
        for n in notifications
    ]

# Получение уведомлений по типу события
def get_notifications_by_type(event_type):
    session = SessionLocal()
    notifications = session.query(Notification).filter(Notification.event_type == event_type).all()
    session.close()
    return [
        {"id": n.id, "event_type": n.event_type, "data": json.loads(n.data), "created_at": n.created_at}
        for n in notifications
    ]

# Получение уведомления по ID
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
    app.run(host="0.0.0.0", port=5000)
