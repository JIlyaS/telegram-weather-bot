from datetime import date, timedelta
from load import data, change_data
from init import bot
import functions
import consts


def add_history_weather(data_weather, text):
    city = text.split(' ')[0]
    day = data_weather[0]['valid_date']
    weather_text = data_weather[0]['weather']['description']

    if city in data['history_weather'] and day not in data['history_weather'][city]:
        data['history_weather'][city][day] = [weather_text]
    elif city not in data['history_weather']:
        data['history_weather'][city] = {}
        data['history_weather'][city][day] = [weather_text]
    elif city in data['history_weather'] and day in data['history_weather'][city]:
        data['history_weather'][city][day].insert(0, weather_text)


def get_history_message(message, city, day):
    user_id = str(message.from_user.id)
    if day.lower() == 'сегодня':
        today = date.today()
        if today.month < 10:
            month = '0' + str(today.month)
        else:
            month = today.month

        if today.day < 10:
            cur_day = '0' + str(today.day)
        else:
            cur_day = today.day

        day_dict = '{0}-{1}-{2}'.format(str(today.year), str(month), str(cur_day))
    elif day.lower() == 'завтра':
        today = date.today() + timedelta(days=1)
        if today.month < 10:
            month = '0' + str(today.month)
        else:
            month = today.month

        if today.day < 10:
            cur_day = '0' + str(today.day)
        else:
            cur_day = today.day

        day_dict = '{0}-{1}-{2}'.format(str(today.year), str(month), str(cur_day))
    else:
        day_dict = day

    if city in data['history_weather']:
        if day_dict in data['history_weather'][city]:
            history_list = data['history_weather'][city][day_dict][0:3]
            weather_text = ''
            for weather in history_list:
                weather_text += weather + '\n'
            bot.send_message(message.chat.id, 'История погоды для города {0}:\n{1}\n\n{2} \nВсего {3} запрос(ов)'.format(city, day_dict, weather_text, str(len(data['history_weather'][city][day_dict]))))
            functions.get_inline_key_city(message.chat.id, consts.CITY_QUESTION)
            change_data('states', user_id, consts.CITY_STATE)
        else:
            functions.get_error_message(message, 'Неизвестная дата погоды!')
    else:
        functions.get_error_message(message, 'Неизвестен город!')
