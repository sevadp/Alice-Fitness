Yandex Lyceum Project

TRANSLATE XD

Skill "My indicators" for Yandex Alice.

Purpose:
Developing Alice Skills, which can be used to quickly and easily retrieve data from
Google Platform FIT. At the moment, you can get basic data: Steps, Minutes of activity, Cardio points.
As well as specialized activity - running, improving this direction can already be
quietly get your time playing tennis or other sports. That is, the base is ready.

Ready modules:
1) Customized API Google app
2) Authorize Google OAuth
3) Saving user data to the database.
5) Raised WEB processing all requests.
6) Communication with Alice with all branches of the development of the dialogue and the transfer of the data.

The essence of communication with Alice:
1) Greetings
2) Request from the user verification code for communication ID YANDEX and Google.
3) This request is obtained on our server http://dpseva.pythonanywhere.com
4) In case of success, we assign a key to the user, according to which we will give results.
5) Next, the request for the type time = response, the output is available.

Database:
1) mongoDB works for Google, keeps everything in memory, logs in json. It is easy to look at errors and TP, if any.
2) BASE JSON - User information is here. Necessary, because FLASK has many workers, each has its own memory.
3) json itself is constantly updated. It is loaded and unloaded. Requires constant contact with her.

Data upload:
1) Currently implemented a one-time download of data from Google.
2) The time is indicated personally. 6 hours / 12 hours / day / 2 days / 3 days / 7 days. / 14 days
3) Uploading is possible only with user permission to give data.

Possible improvements:
1) Store user sessions, if possible, in order not to make repeated logins.
2) Individualize users by assigning each their own secret-key. By which it will be possible
set goals, etc.


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
