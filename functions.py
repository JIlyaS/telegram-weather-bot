from datetime import date, timedelta, datetime
import os
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import requests

from load import data, change_data
from init import bot
from history import add_history_weather
import consts


def get_request_data(message, city):
    token = os.environ["WEATHER_KEY"]
    res = requests.get(data["weather_api"] + '/forecast/daily', params={'city': city, 'key': token, 'lang': 'ru'})
    if res.status_code == 200:
        return res.json()
    else:
        get_error_message(message, consts.ERROR_MESSAGE)
        return


def get_result_message(message, month, day, degrees, weather_text):
    bot.send_message(message.chat.id, '[Месяц: {0}, день: {1}, температура: {2}, минимальная (по ощущениям): {3}, максимальная (по ощущениям): {4}]: {5}'.format(month, day, degrees["temp"], degrees["app_max_temp"], degrees["app_min_temp"], weather_text))


def generate_weather_message(current_data, message, message_text):
    add_history_weather(current_data, message_text)
    weather_text = current_data[0]['weather']['description']
    degrees_dict = {"temp": current_data[0]['temp'], "app_max_temp": current_data[0]['app_max_temp'],
                    "app_min_temp": current_data[0]['app_min_temp']}
    time_tuple = datetime.fromtimestamp(current_data[0]['ts']).timetuple()
    month = consts.MONTHS[time_tuple[1] - 1]
    day = time_tuple[2]
    get_result_message(message, month, day, degrees_dict, weather_text)


def get_fix_date_weather(message, data_weather, weather_word):
    today = date.today()
    if weather_word == 'завтра':
        today = date.today() + timedelta(days=1)
    if data_weather:
        current_data = [item for item in data_weather['data'] if int(item['valid_date'].split('-')[2]) == int(today.day)]
        generate_weather_message(current_data, message, message.text)
    else:
        get_error_message(message, consts.ERROR_MESSAGE)


def get_inline_key_weather(chat_id, message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(InlineKeyboardButton("Сегодня", callback_data="now"), InlineKeyboardButton("Завтра", callback_data="tomorrow"))
    bot.send_message(chat_id, message, reply_markup=markup)


def get_error_message(message, text, st=consts.MAIN_STATE):
    user_id = str(message.from_user.id)
    if st == consts.MAIN_STATE:
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
        markup.row(*consts.START_KEYBOARD_LIST)
        bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        bot.reply_to(message, text)
    change_data('states', user_id, st)


def get_inline_key_city(chat_id, message):
    markup = InlineKeyboardMarkup(row_width=2)
    inline_btn_array = []

    for index, city in enumerate(data['cities']):
        inline_btn_array.append(InlineKeyboardButton(city[str(index)], callback_data=str(index)))
    markup.row(*inline_btn_array)

    bot.send_message(chat_id, message, reply_markup=markup)

def get_keyboard_return(chat_id, message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row(*consts.RETURN_KEYBOARD_LIST)
    bot.send_message(chat_id, message, reply_markup=markup)
