Yandex Lyceum Project

Навык "Мои показатели" для Яндекс Алисы.

Цель: 
Разработка Навыка Алисы, с помощью которого можно будет получить быстро и легко данные из
платформы Google FIT. В данный момент можно получить базовые данные: Шаги, Минуты активности, Баллы кардио.
А так же специализированная активность - бег, улучшая данное направление можно уже будет
спокойно получать время занятия теннисом или другими видами спорта. То есть база готова.

Готовые модули: 
1) Настроенное API приложение Google
2) Авторизация Google OAuth
3) Сохранение данных пользователя в базу данных.
5) Поднятый WEB, обрабатывающий все запросы.
6) Общение с Алисой со всеми ветками развития диалога и передачей полученных данных.

Суть общения с Алисой:
1) Приветствие
2) Запрос у пользователя верификационного кода, для связи ID YANDEX и Google.
3) Данный запрос получается на нашем же сервере http://dpseva.pythonanywhere.com
4) В случае успеха мы закрепляем за пользователем ключ, по которому будем давать результаты.
5) Далее запрос на тип + время = ответ, доступен Выход.

База данных:
1) mongoDB работает для Google, держит все в памяти, логирует в json. Легко смотреть на ошибки и тп, если возникнут.
2) BASE JSON - Информация о пользователях лежит здесь. Необходима, т.к FLASK имеет много воркеров, у каждого своя память.
3) Постоянно обновляется и сам json. Подгружается и выгружается. Требуется постоянный контакт с ней.

Выгрузка данных:
1) В данный момент реализованна разовая выгрузка данных из Google.
2) Время указывается самолично. 6 часов / 12 часов / сутки / 2 суток / 3 суток / 7 дн. / 14 дн. 
3) Выгрузка возможна только при разрешении пользователя давать данные.

Возможные улучшения:
1) Хранить сессии юзеров, если возможно, чтобы не делать повторных авторизаций.
2) Индивидуализировать пользователей, присвоив каждому свой secret-key. По которому можно будет
ставить себе цели и т.п.


License Google
https://developers.google.com/terms/
https://developers.google.com/fit/terms


Copyright (c) 2019 Vsevolod Zakhryapin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
