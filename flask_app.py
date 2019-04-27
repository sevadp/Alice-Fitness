from flask import Flask, request, redirect
from oauth import OAuthSession
import logging
from mongoAccess import FitnessDatabase
import random
from datetime import timedelta
import json

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

#######
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
#######

sessionStorage = {}
keys = {}


def get_json():
    global sessionStorage
    global keys
    with open("data/sessionStorage.json", "r") as fp:
        sessionStorage = json.load(fp)
    with open("data/stats.json", "r") as fp:
        keys = json.load(fp)


def save_json():
    global sessionStorage
    global keys
    with open("data/sessionStorage.json", "w") as fp:
        sessionStorage = json.dump(sessionStorage, fp)
    with open("data/stats.json", "w") as fp:
        keys = json.dump(keys, fp)


# Веб!
@app.route('/')
def index():
    return redirect('http://dpseva.pythonanywhere.com/auth')


@app.route('/auth')
def authorize():
    print('Started AUTH')
    return OAuthSession.authorize()


@app.route('/auth_success')
def auth_success():
    get_json()
    session = OAuthSession()
    session.callback()
    db = FitnessDatabase(session)
    db.update()
    rd = []
    for i in keys.keys():
        rd.append(int(i))
    key = random.randint(100000, 999999)
    while key in rd:
        key = random.randint(100000, 999999)
    formatted_string = "Укажи код верификации в приложении Алиса: " + str(key)
    keys[key] = {"steps": [], "activity": [], "health": [], "running": []}
    print()
    logging.info("AUTH STARTED")
    logging.info(str(keys))
    print()
    for i in range(len(FitnessDatabase.timeQueries)):
        keys[key]["steps"].append(db.steps(i))
        keys[key]["activity"].append(db.activity_minutes(i))
        keys[key]["health"].append(db.heart_minutes(i))
        keys[key]["running"].append(db.running_time_ms(i))
    save_json()
    return formatted_string


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    print()
    logging.info("СОСТОЯНИЕ БАЗЫ ДАННЫХ! ВНИМАНИЕ!")
    logging.info(sessionStorage)
    print()

    logging.info('Response: %r', request.json)
    save_json()

    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    get_json()

    if req['session']['new']:

        sessionStorage[user_id] = {
            'suggests': [
                "Авторизовать",
            ],
            'auth': 0,
            'key': 0,
        }
        res['response']['text'] = 'Привет! Введи "Авторизовать", чтобы продолжить.'
        res['response']['buttons'] = get_suggests(user_id)
        return

    if req['request']['original_utterance'].lower() == "выход":
        sessionStorage[user_id] = {
            'suggests': [
                "Авторизовать",
            ],
            'auth': 0,
            'key': 0,
        }
        res['response']['text'] = 'Пока!'
        res[ 'response' ]['end_session'] = True
        res['response']['buttons'] = get_suggests(user_id)
        return

    if req['request']['original_utterance'].lower() in ['авторизовать'] and sessionStorage[user_id]['auth'] == 0:

        res['response']['text'] = "Привяжите свой аккаунт к GOOGLE FIT > " + "http://dpseva.pythonanywhere.com!" + \
                                  " А далее запиши свой КОД ВЕРИФИКАЦИИ!"

        sessionStorage[user_id] = {
            'suggests': [
                "Выход",
            ],
            'auth': -1,
            'key': 0,
        }
        res['response']['buttons'] = get_suggests(user_id)
        return

    elif sessionStorage[user_id]['auth'] == 0:
        sessionStorage[user_id] = {
            'suggests': [
                "Авторизовать",
            ],
            'auth': 0,
            'key': 0,
        }
        res['response']['text'] = 'Попробуйте еще раз! Введи "Авторизовать", чтобы продолжить.'
        res['response']['buttons'] = get_suggests(user_id)
        return

    if sessionStorage[user_id]['auth'] == -1:
        init = req['request']['original_utterance'].lower()
        print(init)
        print(keys.keys())
        if init in keys.keys():
                res['response']['text'] = "Авторизация успешна! Для получения статистики введите: Шаги, Активность, " \
                                          "Сердце, Минуты бега!"

                sessionStorage[user_id] = {
                    'suggests': [
                        "Шаги",
                        "Активность",
                        "Сердце",
                        "Минуты бега",
                        "Выход"
                    ],
                    'auth': 1,
                    'key': init,
                }
                res['response']['buttons'] = get_suggests(user_id)
                return
        else:
                res['response']['text'] = "Код не верный! Введи еще раз!"

                sessionStorage[user_id] = {
                    'suggests': [
                        "Выход",
                    ],
                    'auth': -1,
                    'key': 0,
                }
                res['response']['buttons'] = get_suggests(user_id)
                return
    if sessionStorage[user_id]['auth'] == 1:
        sessionStorage[user_id] = {
            'suggests': [
                "Шаги",
                "Активность",
                "Сердце",
                "Минуты бега",
                "Выход"
            ],
            'auth': 1,
            'key': sessionStorage[user_id]['key'],
        }
        res['response']['buttons'] = get_suggests(user_id)
        st = keys[sessionStorage[user_id]['key']]
        if req['request']['original_utterance'].lower() == "шаги":
            res['response']['text'] = "Ваша статистика за 6, 12, 24, 48, 72 144, 288 часа : " + str(
                st["steps"][0]) + ", " + str(st["steps"][1]) + ", " + str(st["steps"][2]) + ", " + str(
                st["steps"][3]) + ", " + str(st["steps"][4]) + ", " + str(st["steps"][5]) + ", " + str(st["steps"][6])
            return
        elif req['request']['original_utterance'].lower() == "активность":
            res['response']['text'] = "Ваша статистика за 6, 12, 24, 48, 72 144, 288 часа : " + str(
                st["activity"][0]) + ", " + str(st["activity"][1]) + ", " + str(st["activity"][2]) + ", " + str(
                st["activity"][3]) + ", " + str(st["activity"][4]) + ", " + str(st["activity"][5]) + ", " + str(
                st["activity"][6])
            return
        elif req['request']['original_utterance'].lower() == "сердце":
            res['response']['text'] = "Ваша статистика за 6, 12, 24, 48, 72 144, 288 часа : " + str(
                st["health"][0]) + ", " + str(st["health"][1]) + ", " + str(st["health"][2]) + ", " + str(
                st["health"][3]) + ", " + str(st["health"][4]) + ", " + str(st["health"][5]) + ", " + str(
                st["health"][6])
            return
        elif req['request']['original_utterance'].lower() == "минуты бега":
            res['response']['text'] = "Ваша статистика за 6, 12, 24, 48, 72 144, 288 часа : " + str(
                timedelta(milliseconds=st["running"][0])) + ", " + str(timedelta(milliseconds=st["running"][1])) +\
                                      ", " + str(timedelta(milliseconds=st["running"][2])) + ", " + str(
                timedelta(milliseconds=st["running"][3])) + ", " + str(timedelta(milliseconds=st["running"][4])) +\
                                      ", " + str(timedelta(milliseconds=st["running"][5])) + ", " + str(
                timedelta(milliseconds=st["running"][6]))
            return
        elif req['request']['original_utterance'].lower() == "выход":
            res['response']['end_session'] = True
            res['response']['text'] = "Пока!"
            return
        else:
            res['response']['text'] = "Попробуйте снова!"
            return


def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests']
    ]

    session['suggests'] = session['suggests']
    sessionStorage[user_id] = session

    return suggests


if __name__ == '__main__':
    logging.info("Script Started")
    app.run()

    app.run(debug=True)