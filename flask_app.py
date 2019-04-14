import json
from flask import Flask, redirect, request, url_for
import logging
from oauth import OAuthSession
from mongoAccess import FitnessDatabase
import random
from datetime import timedelta

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
ssss = {"web":{
  "client_id":"704405267037-7dplj60oku5bi24a1ul5tam0ggmms3uv.apps.googleusercontent.com",
  "authorize_url":"https://accounts.google.com/o/oauth2/auth",
  "access_token_url":"https://oauth2.googleapis.com/token",
  "client_secret": "acuoPUfbZwotI_CycNGAyyX0"
},
  "unused": {
    "auth_uri":"https://accounts.google.com/o/oauth2/auth",
  "token_uri":"https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
  "redirect_uris":["http://localhost:5000"],
  "javascript_origins":["http://localhost:5000"]
  }
}
app.config['OAUTH_CREDENTIALS'] = ssss['web']
app.config['SECRET_KEY'] = 'top secret!'

# Сессии Алисы
sessionStorage = {}
base = {}
stats = {}


@app.route('/post', methods=[ 'POST' ])
def main():
    logging.info('Request: %r', request.json)

    # Начинаем формировать ответ, согласно документации
    # мы собираем словарь, который потом при помощи библиотеки json
    # преобразуем в JSON и отдадим Алисе
    response = {
        'session': request.json[ 'session' ],
        'version': request.json[ 'version' ],
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
    return url_for('authorize', _external=True) # url_for принимает название метода


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
    key = random.randint(1000, 9999)
    formatted_string = str(key)
    stats[key] = [db.steps(), db.activity_minutes(), db.heart_minutes(), timedelta(milliseconds=db.running_time_ms())]
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
    user_id = req[ 'session' ][ 'user_id' ]

    if req[ 'session' ][ 'new' ]:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        # Запишем подсказки, которые мы ему покажем в первый раз

        sessionStorage[ user_id ] = {
            'suggests': ["0"],
            "auth": 0,
            "key": -1,
        }
        # Заполняем текст ответа
        res[ 'response' ][ 'text' ] = 'Привет! Введи "Авторизовать", чтобы продолжить.'
        # Получим подсказки
        res[ 'response' ][ 'buttons' ] = create_suggs(user_id)
        return

    if req['request']['original_utterance'].lower() == "авторизовать" and sessionStorage[user_id]["auth"] == 0:
        # Авторизация гугла
        res['response']['text'] = "Привяжите свой аккаунт к GOOGLE FIT > " + "http://sevadp.pythonanywhere.com !" \
                                                                             " А далее запиши свой КОД ВЕРИФИКАЦИИ!"
        sessionStorage[user_id]["suggests"] = ["Авторизоваться", "Выход"]
        sessionStorage[user_id]["auth"] = -1
        res['response']['buttons'] = create_suggs(user_id)
        return
    elif sessionStorage[user_id]["auth"] == -1:
        if int(req['request']['original_utterance'].lower()) in stats.keys():
            logging.info('INFO: Test Auth')
            sessionStorage[user_id]["key"] = int(req['request']['original_utterance'].lower())
            # base[sessionStorage[user_id]["key"]] = {"steps": stats[res['response']['text']]["steps"],
            #                                         "activity_minutes": stats[res['response']['text']]["activity_minutes"],
            #                                         "heart": stats[res['response']['text']]["heart"],
            #                                         "running": stats[res['response']['text']]["running"]}
            res['response']['text'] = ("Авторизация успешна! Действуйте дальше!")
            sessionStorage[user_id]["suggests"] = ["Шаги", "Активность", "Сердце", "Бег", "Выход"]
            res['response']['buttons'] = create_suggs(user_id)
            sessionStorage[user_id]["auth"] = 1
            return
        else:
            res['response']['text'] = "Авторизация не успешна! Вышлите КОД с http://sevadp.pythonanywhere.com!"
            sessionStorage[user_id]["suggests"] = ["Авторизоваться", "Выход"]
            sessionStorage[user_id]["auth"] = -1
            res['response']['buttons'] = create_suggs(user_id)
            return
    # elif req['request']['original_utterance'].lower() != "0" and sessionStorage[user_id]["auth"] == 0:
    #    res['response']['text'] = "Данный раздел временно не работает!"

    if sessionStorage[user_id]["auth"] == 1:
        if req[ 'request' ][ 'original_utterance' ].lower() == "шаги":
            res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][0])
            res['response']['buttons'] = create_suggs(user_id)
        elif req[ 'request' ][ 'original_utterance' ].lower() == "активность":
            print(1)
        elif req['request']['original_utterance'].lower() == "сердце":
            print(2)
        elif req['request']['original_utterance'].lower() == "бег":
            print(3)
        else:
            res['response']['text'] = "Попробуйте снова!"
            res['response']['buttons'] = create_suggs(user_id)
            return
    # Сюда дойдем только, если пользователь не новый,
    # и разговор с Алисой уже был начат
    # Обрабатываем ответ пользователя.
    # В req['request']['original_utterance'] лежит весь текст,
    # что нам прислал пользователь
    # Если он написал 'ладно', 'куплю', 'покупаю', 'хорошо',
    # то мы считаем, что пользователь согласился.
    # Подумайте, всё ли в этом фрагменте написано "красиво"?
    # if req[ 'request' ][ 'original_utterance' ].lower() in [
    #    'ладно',
    #    'куплю',
    #    'покупаю',
    #   'хорошо'
    # ]:
    #    # Пользователь согласился, прощаемся.
    #    res[ 'response' ][ 'text' ] = 'Слона можно найти на Яндекс.Маркете!'
    #    res[ 'response' ][ 'end_session' ] = True
    #    return

    # Если нет, то убеждаем его купить  слона!
    # res[ 'response' ][ 'text' ] = 'Все говорят "%s", а ты купи слона!' % (
    #    req[ 'request' ][ 'original_utterance' ]
    # )
    # res[ 'response' ][ 'buttons' ] = get_suggests(user_id)


# Функция возвращает две подсказки для ответа.

def create_suggs(user_id):
    session = sessionStorage[user_id]["suggests"]

    suggs = []

    for i in session:
        suggs.append({"title": i, "hide": True})

        if suggs[-1]["title"] == "Авторизовать":
            suggs[-1]["url"] = "http://sevadp.pythonanywhere.com"
        elif suggs[-1]["title"] == "Выйти":
            sessionStorage[user_id]["auth"] = 0

    return suggs


if __name__ == '__main__':
    app.run(debug=True)