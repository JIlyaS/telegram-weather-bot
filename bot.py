from telebot.types import ReplyKeyboardMarkup
import functions
from history import get_history_message
from load import data, change_data
from init import bot
import consts


@bot.message_handler(commands=['start'])
def send_welcome(message):
    functions.get_main_keyboard(message.chat.id, 'Привет. Это бот-погода. Поможет узнать погоду в любом городе.')


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, 'Форматы ввода: "Город" -> "Дата", ' +
                                      '"Город Дата", "История Город Дата". ' +
                                      'Дату можно обозначать ключевыми словами: "сегодня" или "завтра". ' +
                                      'Внимание! Дату можно указывать до 16 дней вперёд.' +
                                      'Узнать историю запросов в систему можно с помощью команды: ' +
                                      'История {Название города} {дата}. Дата в формате: 2020-05-05 ' +
                                      'или с помощью ключевых слов "сегодня" или "завтра"')


@bot.message_handler(func=lambda message: data['states'].get(str(message.from_user.id), consts.MAIN_STATE) == consts.MAIN_STATE)
def main_handler(message):
    user_id = str(message.from_user.id)
    if message.text == 'Погода':
        functions.get_keyboard_return(message.chat.id, 'Теперь вы можете выбрать город, который вас инетерсует или вернуться на главную!')
        functions.get_inline_key_city(message.chat.id, 'Какой город вас интересует?')
        change_data('states', user_id, consts.CITY_STATE)
    elif message.text == 'Настройки':
        functions.get_keyboard_return(message.chat.id, 'Теперь вы можете добавить город в избранное!')
        bot.send_message(message.chat.id, 'Добавьте избранный город для быстрого выбора. Напишите полное название города.')
        change_data('states', user_id, consts.SETTINGS_STATE)
    else:
        functions.get_error_message(message, consts.ERROR_MESSAGE)


@bot.message_handler(func=lambda message: data['states'].get(str(message.from_user.id), consts.MAIN_STATE) == consts.CITY_STATE)
def city_handler(message):
    user_id = str(message.from_user.id)
    if message.text == 'На главную':
        functions.get_main_keyboard(message.chat.id, 'Выберите пункт меню.')
        change_data('states', user_id, consts.MAIN_STATE)
    elif len(message.text.split(' ')) == 1:
        resp = functions.get_request_data(message, message.text)
        data['city_weather']['city'] = resp
        data['city_weather']['city_name'] = message.text
        functions.get_inline_key_weather(message.chat.id, 'На какую дату? Формат даты: "Месяц, число" или ключевые слова: "сегодня, завтра"')
        change_data('states', user_id, consts.WEATHER_DATE_STATE)
    elif len(message.text.split(' ')) == 2:
        message_arr = message.text.split(' ')
        if message_arr[-1].lower() == 'сегодня':
            resp = functions.get_request_data(message, message_arr[0])
            functions.get_fix_date_weather(message, resp, message_arr[-1].lower())
            functions.get_inline_key_city(message.chat.id, consts.CITY_QUESTION)
        elif message_arr[-1].lower() == 'завтра':
            resp = functions.get_request_data(message, message_arr[0])
            functions.get_fix_date_weather(message, resp, message_arr[-1].lower())
            functions.get_inline_key_city(message.chat.id, consts.CITY_QUESTION)
        else:
            functions.get_error_message(message, consts.ERROR_MESSAGE)
    elif message.text.split(' ')[0] == 'История':
        message_parsed = message.text.split(' ')
        if len(message_parsed) == 1 or len(message_parsed) == 2:
            functions.get_error_message(message, 'Неверен формат ввода для показа истории погоды')
        else:
            city = message.text.split(' ')[1]
            day = message.text.split(' ')[2]
            get_history_message(message, city, day)
    else:
        functions.get_error_message(message, consts.ERROR_MESSAGE)


@bot.message_handler(func=lambda message: data['states'].get(str(message.from_user.id), consts.MAIN_STATE) == consts.SETTINGS_STATE)
def settings_handler(message):
    user_id = str(message.from_user.id)
    if message.text == 'На главную':
        functions.get_main_keyboard(message.chat.id, 'Выберите пункт меню.')
        change_data('states', user_id, consts.MAIN_STATE)
    elif functions.get_request_data(message, message.text):
        if message.text not in data['cities']:
            index = str(len(data['cities']))
            data['cities'].append({index: message.text})
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
            markup.row(*consts.START_KEYBOARD_LIST)
            bot.send_message(message.chat.id, 'Город успешно добавлен в избранное.', reply_markup=markup)
        else:
            functions.get_error_message(message, 'Город уже добавлен в избранное!')
    else:
        functions.get_error_message(message, consts.ERROR_MESSAGE)
    change_data('states', user_id, consts.MAIN_STATE)


@bot.message_handler(func=lambda message: data['states'].get(str(message.from_user.id), consts.MAIN_STATE) == consts.WEATHER_DATE_STATE)
def weather_date_handler(message):
    user_id = str(message.from_user.id)
    if message.text == 'На главную':
        bot.send_message(message.chat.id, 'Выберите пункт меню.')
        change_data('states', user_id, consts.MAIN_STATE)
    elif message.text.lower() == 'сегодня':
        functions.get_fix_date_weather(message, data['city_weather']['city'], message.text.lower())
        functions.get_inline_key_city(message.chat.id, consts.CITY_QUESTION)
        change_data('states', user_id, consts.CITY_STATE)
        data['city_weather']['city'] = {}
    elif message.text.lower() == 'завтра':
        functions.get_fix_date_weather(message, data['city_weather']['city'], message.text.lower())
        functions.get_inline_key_city(message.chat.id, consts.CITY_QUESTION)
        change_data('states', user_id, consts.CITY_STATE)
        data['city_weather']['city'] = {}
    elif message.text.split(',')[0].strip().lower() in consts.MONTHS:
        if ',' not in message.text or not message.text.split(',')[1]:
            functions.get_error_message(message, 'Неверная дата, повторите запрос!')
            return
        month, day = message.text.split(',')
        day = int(day.strip())

        if data['city_weather']['city']:
            current_data = [item for item in data['city_weather']['city']['data'] if
                            int(item['valid_date'].split('-')[2]) == day]
        else:
            functions.get_error_message(message, 'Неверный ввод данных! Я тебя не понял!')
            return

        if current_data:
            message_str = data['city_weather']['city_name'] + ' ' + message.text
            functions.generate_weather_message(current_data, message, message_str)
        else:
            functions.get_error_message(message, 'Вы вышли за границу допустимых значений, повторите запрос!')
            return
        functions.get_inline_key_city(message.chat.id, consts.CITY_QUESTION)
        change_data('states', user_id, consts.CITY_STATE)
        data['city_weather']['city'] = {}
    else:
        functions.get_error_message(message, consts.ERROR_MESSAGE)


@bot.callback_query_handler(func=lambda call: call)
def callback_handler(call):
    user_id = str(call.from_user.id)
    if call.data == 'now':
        functions.get_fix_date_weather(call.message, data['city_weather']['city'], "сегодня")
        functions.get_inline_key_city(call.message.chat.id, consts.CITY_QUESTION)
        change_data('states', user_id, consts.CITY_STATE)
        data['city_weather']['city'] = {}
    elif call.data == 'tomorrow':
        functions.get_fix_date_weather(call.message, data['city_weather']['city'], "завтра")
        functions.get_inline_key_city(call.message.chat.id, consts.CITY_QUESTION)
        change_data('states', user_id, consts.CITY_STATE)
        data['city_weather']['city'] = {}
    else:
        for index, city in enumerate(data['cities']):
            if str(call.data) == str(index):
                bot.send_message(call.message.chat.id, city[str(index)])
                bot.answer_callback_query(call.id, 'Ожидание...')
                resp = functions.get_request_data(call.message, city[str(index)])
                data['city_weather']['city'] = resp
                data['city_weather']['city_name'] = city[str(index)]
                functions.get_inline_key_weather(call.message.chat.id,
                                       'На какую дату? Формат даты: "Месяц, число" или ключевые слова: "сегодня, завтра"')
                change_data('states', user_id, consts.WEATHER_DATE_STATE)


if __name__ == '__main__':
    bot.polling()
