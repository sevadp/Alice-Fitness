# импортируем библиотеки
from flask import Flask, request
import logging
import random

# библиотека, которая нам понадобится для работы с JSON
import json

# создаём приложение
# мы передаём __name__, в нём содержится информация,
# в каком модуле мы находимся.
# В данном случае там содержится '__main__',
# так как мы обращаемся к переменной из запущенного модуля.
# если бы такое обращение, например, произошло внутри модуля logging,
# то мы бы получили 'logging'
app = Flask(__name__)

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# Создадим словарь, чтобы для каждой сессии общения с навыком хранились
# подсказки, которые видел пользователь.
# Это поможет нам немного разнообразить подсказки ответов
# (buttons в JSON ответа).
# Когда новый пользователь напишет нашему навыку, то мы сохраним
# в этот словарь запись формата
# sessionStorage[user_id] = {'suggests': ["Не хочу.", "Не буду.", "Отстань!"]}
# Такая запись говорит, что мы показали пользователю эти три подсказки.
# Когда он откажется купить слона,
# то мы уберем одну подсказку. Как будто что-то меняется :)
sessionStorage = {}
base = {}


@app.route('/post', methods=[ 'POST' ])
# Функция получает тело запроса и возвращает ответ.
# Внутри функции доступен request.json - это JSON,
# который отправила нам Алиса в запросе POST
def main():
    get_json()
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
    save_json()
    return json.dumps(response)


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
        res[ 'response' ][ 'text' ] = 'Привет! Введи свой секретный ключ! Если ты новенький, введи 0.'
        # Получим подсказки
        res[ 'response' ][ 'buttons' ] = create_suggs(user_id)
        return

    if req['request']['original_utterance'].lower() == "0" and sessionStorage[user_id]["auth"] == 0:
        auth_google()
        create_user(user_id)
    elif req['request']['original_utterance'].lower() != "0" and sessionStorage[user_id]["auth"] == 0:
        if check_auth(req['request']['original_utterance']):
            sessionStorage[user_id]["key"] = req['request']['original_utterance']

    if sessionStorage[user_id]["auth"] == 1:
        if req[ 'request' ][ 'original_utterance' ].lower() == "x1":
            get_x1()
        elif req[ 'request' ][ 'original_utterance' ].lower() == "x2":
            get_x2()
        elif req['request']['original_utterance'].lower() == "x3":
            get_x3()
        elif req['request']['original_utterance'].lower() == "x4":
            get_x4()
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

    return suggs


def get_suggests(user_id):
    session = sessionStorage[ user_id ]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session[ 'suggests' ][ :2 ]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session[ 'suggests' ] = session[ 'suggests' ][ 1: ]
    sessionStorage[ user_id ] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })

    return suggests


def check_auth(key):
    if key in base.keys():
        return True


def create_user(user_id):
    new_key = random.randint(10000000, 99999999)
    while new_key in base.keys():
        new_key = random.randint(10000000, 99999999)
    base[new_key] = 0
    sessionStorage[user_id]["key"] = new_key


def get_json():
    global base
    with open("data.json", "r") as fp:
        base = json.load(fp)


def save_json():
    global base
    with open("data.json", "r") as fp:
        base = json.load(fp)


if __name__ == '__main__':
    app.run()