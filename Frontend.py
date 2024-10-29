# frontend.py
import telebot
from telebot import types
from bot import bot  # импорт бота из bot.py
from Backend import add_user, remove_user  # импорт функций для работы с базой данных

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
    add_user(chat_id, 'all')  # Добавляем пользователя в базу данных

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
    remove_user(chat_id)  # Удаляем пользователя из базы данных

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
