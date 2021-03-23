import json
import consts

data = {}

try:
    data = json.load(open('db/data.json', 'r', encoding='utf-8'))
except FileNotFoundError:
    data = {
        "token": "1673485604:AAHHwK3mfal0ITHT9V50OAMoSBnG2ER4da0",
        "weather_key": "9f254c735ad3417791385f3af65f8f75",
        "weather_api": "https://api.weatherbit.io/v2.0",
        "states": {},
        "cities": [],
        "history_weather": {},
        "city_weather": {},
        consts.MAIN_STATE: {},
        consts.CITY_STATE: {},
        consts.WEATHER_DATE_STATE: {},
        consts.SETTINGS_STATE: {}
    }


def change_data(key, user_id, value):
    data[key][user_id] = value
    json.dump(data, open('db/data.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
