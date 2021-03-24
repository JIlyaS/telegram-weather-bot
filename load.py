import os
import json
import redis
import consts

redis_url = os.environ.get('REDIS_URL')

init_data = {
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

data = {}

if redis_url is None:
    try:
        data = json.load(open('db/data.json', 'r', encoding='utf-8'))
    except FileNotFoundError:
        data = init_data
else:
    redis_db = redis.from_url(redis_url)
    raw_data = redis_db.get('data')
    if raw_data is None:
        data = init_data
    else:
        data = json.loads(raw_data)


def change_data(key, user_id, value):
    data[key][user_id] = value
    if redis_url is None:
        json.dump(data, open('db/data.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    else:
        redis_db = redis.from_url(redis_url)
        redis_db.set('data', json.dumps(data))
        