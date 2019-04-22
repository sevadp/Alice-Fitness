import datetime
import json
import os
if not os.path.exists('data'):
    os.mkdir('data')

fortnightInS = 14*24*60*60  # две недели в секундах


activities = {
    'Aerobics': 9,
    'Archery': 119,
    'Badminton': 10,
    'Baseball': 11,
    'Basketball': 12,
    'Biathlon': 13,
    'Biking*': 1,
    'Handbiking': 14,
    'Mountain biking': 15,
    'Road biking': 16,
    'Spinning': 17,
    'Stationary biking': 18,
    'Utility biking': 19,
    'Boxing': 20,
    'Calisthenics': 21,
    'Circuit training': 22,
    'Cricket': 23,
    'Crossfit': 113,
    'Curling': 106,
    'Dancing': 24,
    'Diving': 102,
    'Elevator': 117,
    'Elliptical': 25,
    'Ergometer': 103,
    'Escalator': 118,
    'Fencing': 26,
    'Football (American)': 27,
    'Football (Australian)': 28,
    'Football (Soccer)': 29,
    'Frisbee': 30,
    'Gardening': 31,
    'Golf': 32,
    'Guided Breathing': 122,
    'Gymnastics': 33,
    'Handball': 34,
    'HIIT': 114,
    'Hiking': 35,
    'Hockey': 36,
    'Horseback riding': 37,
    'Housework': 38,
    'Ice skating': 104,
    'In vehicle*': 0,
    'Interval Training': 115,
    'Jumping rope': 39,
    'Kayaking': 40,
    'Kettlebell training': 41,
    'Kickboxing': 42,
    'Kitesurfing': 43,
    'Martial arts': 44,
    'Meditation': 45,
    'Mixed martial arts': 46,
    'On foot*': 2,
    'Other (unclassified fitness activity)': 108,
    'P90X exercises': 47,
    'Paragliding': 48,
    'Pilates': 49,
    'Polo': 50,
    'Racquetball': 51,
    'Rock climbing': 52,
    'Rowing': 53,
    'Rowing machine': 54,
    'Rugby': 55,
    'Running*': 8,
    'Jogging': 56,
    'Running on sand': 57,
    'Running (treadmill)': 58,
    'Sailing': 59,
    'Scuba diving': 60,
    'Skateboarding': 61,
    'Skating': 62,
    'Cross skating': 63,
    'Indoor skating': 105,
    'Inline skating (rollerblading)': 64,
    'Skiing': 65,
    'Back-country skiing': 66,
    'Cross-country skiing': 67,
    'Downhill skiing': 68,
    'Kite skiing': 69,
    'Roller skiing': 70,
    'Sledding': 71,
    'Sleeping': 72,
    'Light sleep': 109,
    'Deep sleep': 110,
    'REM sleep': 111,
    'Awake (during sleep cycle)': 112,
    'Snowboarding': 73,
    'Snowmobile': 74,
    'Snowshoeing': 75,
    'Softball': 120,
    'Squash': 76,
    'Stair climbing': 77,
    'Stair-climbing machine': 78,
    'Stand-up paddleboarding': 79,
    'Still (not moving)*': 3,
    'Strength training': 80,
    'Surfing': 81,
    'Swimming': 82,
    'Swimming (open water)': 84,
    'Swimming (swimming pool)': 83,
    'Table tennis (ping pong)': 85,
    'Team sports': 86,
    'Tennis': 87,
    'Tilting (sudden device gravity change)*': 5,
    'Treadmill (walking or running)': 88,
    'Unknown (unable to detect activity)*': 4,
    'Volleyball': 89,
    'Volleyball (beach)': 90,
    'Volleyball (indoor)': 91,
    'Wakeboarding': 92,
    'Walking*': 7,
    'Walking (fitness)': 93,
    'Nording walking': 94,
    'Walking (treadmill)': 95,
    'Walking (stroller)': 116,
    'Waterpolo': 96,
    'Weightlifting': 97,
    'Wheelchair': 98,
    'Windsurfing': 99,
    'Yoga': 100,
    'Zumba': 101
}

runningActivities = [8, 57, 58, 88]


class FitnessDatabase:  # объект для взаимодействия с mongoDB

    propertyNames = {
        "active_minutes": "com.google.active_minutes",
        'heart_minutes': 'com.google.heart_minutes',
        'steps': 'com.google.step_count.delta',
    }

    def __init__(self, oauth_session):  # Метод взаимодействия с синглтоном
        self.oauth_session = oauth_session
        self.current_user = ""

    timeQueries = (  # время запросов в милисекундах
        6 * 60 * 60 * 1000,  # 6 часов
        12 * 60 * 60 * 1000,  # 12 часов
        24 * 60 * 60 * 1000,  # сутки
        2 * 24 * 60 * 60 * 1000,  # два дня
        3 * 24 * 60 * 60 * 1000,  # три дня
        7 * 24 * 60 * 60 * 1000,  # неделя
        14 * 24 * 60 * 60 * 1000,  # две недели
    )

    def update(self):
        self.current_user = self.oauth_session.get(' https://www.googleapis.com/oauth2/v1/'
                                                   'userinfo?alt=json&fields=id')['id']  # получение id пользователя

        record = {  # начало формирования записи
            '_id': self.current_user,
            'data': []
        }
        for timespan in FitnessDatabase.timeQueries:
            record['data'].append(self.data_for_duration(timespan))
        file = open('data/{}.json'.format(self.current_user), 'w')
        file.write(json.dumps(record))
        file.close()

    def data_for_duration(self, duration_in_ms):
        record = {}
        end_time = int(datetime.datetime.now().timestamp() * 1000)
        start_time = end_time - duration_in_ms
        query = {  # шаблон данных запроса
            "aggregateBy": [
                {  # получить все данные по типу: здесь - минуты активности, в цикле подставляются значения из словаря
                    'dataTypeName': 'com.google.active_minutes'
                }],
            "bucketByTime": {"durationMillis": 86400000},  # один день в секундах
            "startTimeMillis": start_time,  # время начала записи
            "endTimeMillis": end_time  # текущее время в мс
        }

        for metric, aggregator in FitnessDatabase.propertyNames.items():  # подсчёт сумм по каждому типу данных
            query['aggregateBy'][0]['dataTypeName'] = aggregator
            response = self.oauth_session.post(
                'https://www.googleapis.com/fitness/v1/users/me/dataset:aggreg'
                'ate?fields=bucket(dataset(point(value(fpVal%2CintVal))))',
                query)  # запрос нужных данных
            counter = 0
            try:
                for bucket in response['bucket']:
                    for dataset in bucket['dataset']:
                        for item in dataset['point']:
                            value = item['value'][0]
                            if 'fpVal' in value:
                                counter += value['fpVal']
                            else:
                                counter += value['intVal']
            except KeyError as err:
                print("QUERY HAS FAIlED:\n", "Exception: {}\n".format(err), response)
                return
            record[metric] = counter
        response = self.oauth_session.get('https://www.googleapis.com/fitness/v1/users/me/sessions?includeDeleted'
                                          '=false&fields=session('
                                          'activeTimeMillis%2CactivityType%2CendTimeMillis%2CstartTimeMillis)')
        running_time_ms = 0
        # todo: начало правок
        for session in response['session']:
            if session['activityType'] in runningActivities:
                if 'endTimeMillis' and 'startTimeMillis' in session:
                    session_end = int(session['endTimeMillis'])
                    session_start = int(session['startTimeMillis'])
                    if session_end >= start_time:
                        timedelta = session_end - max(session_start, start_time)
                        running_time_ms += timedelta

        record['running_time_ms'] = running_time_ms
        return record

    def steps(self, timespan=0):  # запросы к БД
        return json.load(open('data/{}.json'.format(self.current_user)))['data'][timespan]['steps']

    def activity_minutes(self, timespan=0):
        return json.load(open('data/{}.json'.format(self.current_user)))['data'][timespan]['active_minutes']

    def heart_minutes(self, timespan=0):
        return json.load(open('data/{}.json'.format(self.current_user)))['data'][timespan]['heart_minutes']

    def running_time_ms(self, timespan=0):
        return json.load(open('data/{}.json'.format(self.current_user)))['data'][timespan]['running_time_ms']
