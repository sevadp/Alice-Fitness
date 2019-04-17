import json
from flask import Flask, redirect, request, url_for
import logging
from oauth import OAuthSession
from mongoAccess import FitnessDatabase
import random
from datetime import timedelta

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
ssss = {"web": {
    "client_id": "704405267037-7dplj60oku5bi24a1ul5tam0ggmms3uv.apps.googleusercontent.com",
    "authorize_url": "https://accounts.google.com/o/oauth2/auth",
    "access_token_url": "https://oauth2.googleapis.com/token",
    "client_secret": "acuoPUfbZwotI_CycNGAyyX0"
},
    "unused": {
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": ["http://localhost:5000"],
        "javascript_origins": ["http://localhost:5000"]
    }
}
app.config['OAUTH_CREDENTIALS'] = ssss['web']
app.config['SECRET_KEY'] = 'top secret!'

# Сессии Алисы
sessionStorage = {}
base = {}
stats = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    # Начинаем формировать ответ, согласно документации
    # мы собираем словарь, который потом при помощи библиотеки json
    # преобразуем в JSON и отдадим Алисе
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    # Отправляем request.json и response в функцию handle_dialog.
    # Она сформирует оставшиеся поля JSON, которые отвечают
    # непосредственно за ведение диалога
    handle_dialog(request.json, response)

    logging.info('Response: %r', request.json)

    # Преобразовываем в JSON и возвращаем
    return json.dumps(response)


@app.route('/')
def index():
    return redirect('http://dpseva.pythonanywhere.com/auth')


@app.route('/auth')
def authorize():
    print('authorization')
    return OAuthSession.authorize()


@app.route('/auth_success')
def auth_success():
    session = OAuthSession()
    session.callback()
    db = FitnessDatabase(session)
    db.update()
    key = random.randint(100000, 999999)
    while key in stats.keys():
        key = random.randint(100000, 999999)
    formatted_string = "Укажи код верификации в приложении Алиса: " + str(key)
    stats[key] = {"steps": [db.steps(0), db.steps(1), db.steps(2), db.steps(3), db.steps(4), db.steps(5)],
                  "activity": [db.activity_minutes(0), db.activity_minutes(1),
                               db.activity_minutes(2), db.activity_minutes(3),
                               db.activity_minutes(4), db.activity_minutes(5)],
                  "health": [db.heart_minutes(0), db.heart_minutes(1), db.heart_minutes(2), db.heart_minutes(3),
                             db.heart_minutes(4), db.heart_minutes(5)],
                  "running": [db.running_time_ms(0), db.running_time_ms(1), db.running_time_ms(2),
                              db.running_time_ms(3), db.running_time_ms(4), db.running_time_ms(5)]}
    logging.info(str(stats))
    return formatted_string


def get_json():
    global base
    with open("data.json", "r") as fp:
        base = json.load(fp)


def save_json():
    global base
    with open("data.json", "r") as fp:
        base = json.load(fp)


def create_user(user_id):
    new_key = random.randint(10000000, 99999999)
    while new_key in base.keys():
        new_key = random.randint(10000000, 99999999)
    base[new_key] = {}
    sessionStorage[user_id]["key"] = new_key


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        # Запишем подсказки, которые мы ему покажем в первый раз

        sessionStorage[user_id] = {
            'suggests': ["Авторизовать"],
            "auth": 0,
            "key": -1,
        }
        # Заполняем текст ответа
        res['response']['text'] = 'Привет! Введи "Авторизовать", чтобы продолжить.'
        # Получим подсказки
        res['response']['buttons'] = create_suggs(user_id)
        return

    if req['request']['original_utterance'].lower() == "выход":
        res['response']['text'] = "Пока!"
        res['response']['end_session'] = True
        return

    if req['request']['original_utterance'].lower() == "авторизовать" and sessionStorage[user_id]["auth"] == 0:
        # Авторизация гугла
        res['response']['text'] = "Привяжите свой аккаунт к GOOGLE FIT > " + "http://dpseva.pythonanywhere.com!" \
                                                                             " А далее запиши свой КОД ВЕРИФИКАЦИИ!"
        sessionStorage[user_id]["suggests"] = ["Выход"]
        sessionStorage[user_id]["auth"] = -1
        res['response']['buttons'] = create_suggs(user_id)
        return
    elif sessionStorage[user_id]["auth"] == -1:
        if int(req['request']['original_utterance'].lower()) in stats.keys():
            logging.info('INFO: Test Auth')
            sessionStorage[user_id]["key"] = int(req['request']['original_utterance'].lower())
            res['response']['text'] = "Авторизация успешна! Действуйте дальше!"
            sessionStorage[user_id]["suggests"] = ["Шаги", "Активность", "Сердце", "Бег", "Выход"]
            res['response']['buttons'] = create_suggs(user_id)
            sessionStorage[user_id]["auth"] = 1
            return
        else:
            res['response']['text'] = "Авторизация не успешна! Вышлите КОД с http://dpseva.pythonanywhere.com!"
            sessionStorage[user_id]["suggests"] = ["Выход"]
            sessionStorage[user_id]["auth"] = -1
            res['response']['buttons'] = create_suggs(user_id)
            return
    # elif req['request']['original_utterance'].lower() != "0" and sessionStorage[user_id]["auth"] == 0:
    #    res['response']['text'] = "Данный раздел временно не работает!"
    elif sessionStorage[user_id]["auth"] == 0:
        res['response']['text'] = "Попробуйте снова!"
        res['response']['buttons'] = create_suggs(user_id)
        return

    if sessionStorage[user_id]["auth"] == 1:
        st = stats[sessionStorage[user_id]["key"]]
        if req['request']['original_utterance'].lower() == "шаги":
            res['response']['text'] = "Ваша статистика за 6, 12, 24, 48, 72 144 часа : " + str(st["steps"][0]) + ", " + str(st["steps"][1]) + ", " + str(st["steps"][2]) + ", " + str(st["steps"][3]) + ", " + str(st["steps"][4]) + ", " + str(st["steps"][5])
            res['response']['buttons'] = create_suggs(user_id)
            return
        elif req['request']['original_utterance'].lower() == "активность":
            res['response']['text'] = "Ваша статистика за 6, 12, 24, 48, 72 144 часа : " + str(st["activity"][0]) + ", " + str(st["activity"][1]) + ", " + str(st["activity"][2]) + ", " + str(st["activity"][3]) + ", " + str(st["activity"][4]) + ", " + str(st["activity"][5])
            res['response']['buttons'] = create_suggs(user_id)
            return
        elif req['request']['original_utterance'].lower() == "сердце":
            res['response']['text'] = "Ваша статистика за 6, 12, 24, 48, 72 144 часа : " + str(st["health"][0]) + ", " + str(st["health"][1]) + ", " + str(st["health"][2]) + ", " + str(st["health"][3]) + ", " + str(st["health"][4]) + ", " + str(st["health"][5])
            res['response']['buttons'] = create_suggs(user_id)
            return
        elif req['request']['original_utterance'].lower() == "бег":
            res['response']['text'] = "Ваша статистика за 6, 12, 24, 48, 72 144 часа : " + str(st["running"][0]) + ", " + str(st["running"][1]) + ", " + str(st["running"][2]) + ", " + str(st["running"][3]) + ", " + str(st["running"][4]) + ", " + str(st["running"][5])
            res['response']['buttons'] = create_suggs(user_id)
            return
        elif req['request']['original_utterance'].lower() == "выход":
            res['response']['end_session'] = True
            res['response']['text'] = "Пока!"
            return
        else:
            res['response']['text'] = "Попробуйте снова!"
            res['response']['buttons'] = create_suggs(user_id)
            return


def create_suggs(user_id):
    global res
    session = sessionStorage[user_id]["suggests"]

    suggs = []

    for i in session:
        suggs.append({"title": i, "hide": True})

        if suggs[-1]["title"] == "Авторизовать":
            suggs[-1]["url"] = "http://dpseva.pythonanywhere.com"

    return suggs


if __name__ == '__main__':
    app.run(debug=True)