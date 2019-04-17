import json
from flask import Flask, redirect, request
import logging
from oauth import OAuthSession
from mongoAccess import FitnessDatabase
import random

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
    stats[key] = [
        [db.steps(0), db.steps(1), db.steps(2), db.steps(3), db.steps(4), db.steps(5), db.steps(6)],
        [db.activity_minutes(0), db.activity_minutes(1), db.activity_minutes(2),
         db.activity_minutes(3), db.activity_minutes(4), db.activity_minutes(5), db.activity_minutes(6)],
        [db.heart_minutes(0), db.heart_minutes(1), db.heart_minutes(2),
         db.heart_minutes(3), db.heart_minutes(4), db.heart_minutes(5), db.heart_minutes(6)],
        [db.running_time_ms(0), db.running_time_ms(1), db.running_time_ms(2),
         db.running_time_ms(3), db.running_time_ms(4), db.running_time_ms(5), db.running_time_ms(6)]]
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
            "stadium": -1,
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

    if sessionStorage[user_id]["auth"] == 1:
        if sessionStorage[user_id]["stadium"] == -1:
            if req['request']['original_utterance'].lower() == "шаги":
                res['response']['text'] = "Выберите за какой срок!"
                sessionStorage[user_id]["suggests"] = ["6 часов", "12 часов", "24 часа", "2 дня",
                                                       "3 дня", "7 дней", "14 дней", "Выход"]
                res['response']['buttons'] = create_suggs(user_id)
                sessionStorage[user_id]["stadium"] = 1
                return
            elif req['request']['original_utterance'].lower() == "активность":
                res['response']['text'] = "Выберите за какой срок!"
                sessionStorage[user_id]["suggests"] = ["6 часов", "12 часов", "24 часа", "2 дня",
                                                       "3 дня", "7 дней", "14 дней", "Выход"]
                res['response']['buttons'] = create_suggs(user_id)
                sessionStorage[user_id]["stadium"] = 2
                return
            elif req['request']['original_utterance'].lower() == "сердце":
                res['response']['text'] = "Выберите за какой срок!"
                sessionStorage[user_id]["suggests"] = ["6 часов", "12 часов", "24 часа", "2 дня",
                                                       "3 дня", "7 дней", "14 дней", "Выход"]
                res['response']['buttons'] = create_suggs(user_id)
                sessionStorage[user_id]["stadium"] = 3
                return
            elif req['request']['original_utterance'].lower() == "бег":
                res['response']['text'] = "Выберите за какой срок!"
                sessionStorage[user_id]["suggests"] = ["6 часов", "12 часов", "24 часа", "2 дня",
                                                       "3 дня", "7 дней", "14 дней", "Выход"]
                res['response']['buttons'] = create_suggs(user_id)
                sessionStorage[user_id]["stadium"] = 4
                return
            elif req['request']['original_utterance'].lower() == "выход":
                res['response']['end_session'] = True
                res['response']['text'] = "Пока!"
                return
            else:
                res['response']['text'] = "Попробуйте снова!"
                res['response']['buttons'] = create_suggs(user_id)
                return
        if sessionStorage[user_id]["stadium"] < 10:
            if req['request']['original_utterance'].lower() == "6 часов":
                if sessionStorage[user_id]["stadium"] == 1:
                    sessionStorage[user_id]["stadium"] = 10
                elif sessionStorage[user_id]["stadium"] == 2:
                    sessionStorage[user_id]["stadium"] = 20
                elif sessionStorage[user_id]["stadium"] == 3:
                    sessionStorage[user_id]["stadium"] = 30
                elif sessionStorage[user_id]["stadium"] == 4:
                    sessionStorage[user_id]["stadium"] = 40
            if req['request']['original_utterance'].lower() == "12 часов":
                if sessionStorage[user_id]["stadium"] == 1:
                    sessionStorage[user_id]["stadium"] = 11
                elif sessionStorage[user_id]["stadium"] == 2:
                    sessionStorage[user_id]["stadium"] = 21
                elif sessionStorage[user_id]["stadium"] == 3:
                    sessionStorage[user_id]["stadium"] = 31
                elif sessionStorage[user_id]["stadium"] == 4:
                    sessionStorage[user_id]["stadium"] = 41
            if req['request']['original_utterance'].lower() == "24 часа":
                if sessionStorage[user_id]["stadium"] == 1:
                    sessionStorage[user_id]["stadium"] = 12
                elif sessionStorage[user_id]["stadium"] == 2:
                    sessionStorage[user_id]["stadium"] = 22
                elif sessionStorage[user_id]["stadium"] == 3:
                    sessionStorage[user_id]["stadium"] = 32
                elif sessionStorage[user_id]["stadium"] == 4:
                    sessionStorage[user_id]["stadium"] = 42
            if req['request']['original_utterance'].lower() == "2 дня":
                if sessionStorage[user_id]["stadium"] == 1:
                    sessionStorage[user_id]["stadium"] = 13
                elif sessionStorage[user_id]["stadium"] == 2:
                    sessionStorage[user_id]["stadium"] = 23
                elif sessionStorage[user_id]["stadium"] == 3:
                    sessionStorage[user_id]["stadium"] = 33
                elif sessionStorage[user_id]["stadium"] == 4:
                    sessionStorage[user_id]["stadium"] = 43
            if req['request']['original_utterance'].lower() == "3 дня":
                if sessionStorage[user_id]["stadium"] == 1:
                    sessionStorage[user_id]["stadium"] = 14
                elif sessionStorage[user_id]["stadium"] == 2:
                    sessionStorage[user_id]["stadium"] = 24
                elif sessionStorage[user_id]["stadium"] == 3:
                    sessionStorage[user_id]["stadium"] = 34
                elif sessionStorage[user_id]["stadium"] == 4:
                    sessionStorage[user_id]["stadium"] = 44
            if req['request']['original_utterance'].lower() == "7 дней":
                if sessionStorage[user_id]["stadium"] == 1:
                    sessionStorage[user_id]["stadium"] = 15
                elif sessionStorage[user_id]["stadium"] == 2:
                    sessionStorage[user_id]["stadium"] = 25
                elif sessionStorage[user_id]["stadium"] == 3:
                    sessionStorage[user_id]["stadium"] = 35
                elif sessionStorage[user_id]["stadium"] == 4:
                    sessionStorage[user_id]["stadium"] = 45
            if req['request']['original_utterance'].lower() == "14 дней":
                if sessionStorage[user_id]["stadium"] == 1:
                    sessionStorage[user_id]["stadium"] = 16
                elif sessionStorage[user_id]["stadium"] == 2:
                    sessionStorage[user_id]["stadium"] = 26
                elif sessionStorage[user_id]["stadium"] == 3:
                    sessionStorage[user_id]["stadium"] = 36
                elif sessionStorage[user_id]["stadium"] == 4:
                    sessionStorage[user_id]["stadium"] = 46
            else:
                res['response']['text'] = "Попробуйте снова!"
                res['response']['buttons'] = create_suggs(user_id)
                return
        if sessionStorage[user_id]["stadium"] >= 10:
            if sessionStorage[user_id]["stadium"] == 10:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][0][0]) + str(" шагов вы совершили "
                                                                                                 "за последние "
                                                                                                 "6 часов!")
            elif sessionStorage[user_id]["stadium"] == 11:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][0][1]) + str(" шагов вы совершили "
                                                                                                 "за последние "
                                                                                                 "12 часов!")
            elif sessionStorage[user_id]["stadium"] == 12:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][0][2]) + str(" шагов вы совершили "
                                                                                                 "за последние"
                                                                                                 " 24 часа!")
            elif sessionStorage[user_id]["stadium"] == 13:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][0][3]) + str(" шагов вы совершили "
                                                                                                 "за последние"
                                                                                                 " 2 дня!")
            elif sessionStorage[user_id]["stadium"] == 14:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][0][4]) + str(" шагов вы совершили "
                                                                                                 "за последние "
                                                                                                 "3 дня!")
            elif sessionStorage[user_id]["stadium"] == 15:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][0][5]) + str(" шагов вы совершили "
                                                                                                 "за последние "
                                                                                                 "7 дней!")
            elif sessionStorage[user_id]["stadium"] == 16:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][0][6]) + str(" шагов вы совершили "
                                                                                                 "за последние "
                                                                                                 "две недели!")
            elif sessionStorage[user_id]["stadium"] == 20:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][1][0]) + str(" минут активности "
                                                                                                 "за последние"
                                                                                                 " 6 часов!")
            elif sessionStorage[user_id]["stadium"] == 21:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][1][1]) + str(" минут активности "
                                                                                                 "за последние"
                                                                                                 " 12 часов!")
            elif sessionStorage[user_id]["stadium"] == 22:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][1][2]) + str(" минут активности "
                                                                                                 "за последние "
                                                                                                 "24 часа!")
            elif sessionStorage[user_id]["stadium"] == 23:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][1][3]) + str(" минут активности "
                                                                                                 "за последние 2 дня!")
            elif sessionStorage[user_id]["stadium"] == 24:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][1][4]) + str(" минут активности "
                                                                                                 "за последние 3 дня!")
            elif sessionStorage[user_id]["stadium"] == 25:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][1][5]) + str(" минут активности "
                                                                                                 "за последние"
                                                                                                 " 7 дней!")
            elif sessionStorage[user_id]["stadium"] == 26:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][1][6]) + str(" минут активности "
                                                                                                 "за последние"
                                                                                                 " две недели!")
            elif sessionStorage[user_id]["stadium"] == 30:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][2][0]) + str(" баллов кардио "
                                                                                                 "за последние"
                                                                                                 " 6 часов!")
            elif sessionStorage[user_id]["stadium"] == 31:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][2][1]) + str(" баллов кардио "
                                                                                                 "за последние"
                                                                                                 " 12 часов!")
            elif sessionStorage[user_id]["stadium"] == 32:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][2][2]) + str(" баллов кардио "
                                                                                                 "за последние "
                                                                                                 "24 часа!")
            elif sessionStorage[user_id]["stadium"] == 33:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][2][3]) + str(" минут активности "
                                                                                                 "за последние 2 дня!")
            elif sessionStorage[user_id]["stadium"] == 34:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][2][4]) + str(" минут активности "
                                                                                                 "за последние 3 дня!")
            elif sessionStorage[user_id]["stadium"] == 35:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][2][5]) + str(" баллов кардио "
                                                                                                 "за последние"
                                                                                                 " 7 дней!")
            elif sessionStorage[user_id]["stadium"] == 36:
                res['response']['text'] = str(stats[sessionStorage[user_id]["key"]][2][6]) + str(" баллов кардио "
                                                                                                 "за последние"
                                                                                                 " две недели!")
            elif sessionStorage[user_id]["stadium"] == 40:
                res['response']['text'] = str(round(stats[sessionStorage[user_id]["key"]][3][0] / 1000 / 60, 2)) \
                                          + str(" минут бега "
                                                "за последние"
                                                " две недели!")
            elif sessionStorage[user_id]["stadium"] == 41:
                res['response']['text'] = str(round(stats[sessionStorage[user_id]["key"]][3][1] / 1000 / 60, 2)) \
                                          + str(" минут бега "
                                                "за последние"
                                                " две недели!")
            elif sessionStorage[user_id]["stadium"] == 42:
                res['response']['text'] = str(round(stats[sessionStorage[user_id]["key"]][3][2] / 1000 / 60, 2)) \
                                          + str(" минут бега "
                                                "за последние"
                                                " две недели!")
            elif sessionStorage[user_id]["stadium"] == 43:
                res['response']['text'] = str(round(stats[sessionStorage[user_id]["key"]][3][3] / 1000 / 60, 2)) \
                                          + str(" минут бега "
                                                "за последние"
                                                " две недели!")
            elif sessionStorage[user_id]["stadium"] == 44:
                res['response']['text'] = str(round(stats[sessionStorage[user_id]["key"]][3][4] / 1000 / 60, 2)) \
                                          + str(" минут бега "
                                                "за последние"
                                                " две недели!")
            elif sessionStorage[user_id]["stadium"] == 45:
                res['response']['text'] = str(round(stats[sessionStorage[user_id]["key"]][3][5] / 1000 / 60, 2)) \
                                          + str(" минут бега "
                                                "за последние"
                                                " две недели!")
            elif sessionStorage[user_id]["stadium"] == 46:
                res['response']['text'] = str(round(stats[sessionStorage[user_id]["key"]][3][6] / 1000 / 60, 2)) \
                                          + str(" минут бега "
                                                "за последние"
                                                " две недели!")

            sessionStorage[user_id]["stadium"] = -1
            sessionStorage[user_id]["suggests"] = ["Шаги", "Активность", "Сердце", "Бег", "Выход"]
            res['response']['buttons'] = create_suggs(user_id)
            return
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
            suggs[-1]["url"] = "http://dpseva.pythonanywhere.com"

    return suggs


if __name__ == '__main__':
    app.run(debug=True)