import json
from flask import Flask, redirect
from oauth import OAuthSession
from mongoAccess import FitnessDatabase
from datetime import timedelta


app = Flask(__name__)
app.config['OAUTH_CREDENTIALS'] = json.load(open("client_secret.json"))['web']
app.config['SECRET_KEY'] = 'top secret!'
# app.config['SERVER_NAME'] = 'lvh.me:5000'

@app.route('/')
def index():
    print('authorization')
    return OAuthSession.authorize()


@app.route('/auth_success')
def auth_success():
    session = OAuthSession()
    session.callback()
    db = FitnessDatabase(session)
    db.update()
    formatted_string = ""
    for i in range(len(FitnessDatabase.timeQueries)):
        formatted_string += "Hello, user. You have walked {} steps in the past two weeks;" \
                       " also you've got {} active and {} heart minutes. you have been running for {} on record</br>". \
            format(db.steps(i),
                   db.activity_minutes(i),
                   db.heart_minutes(i),
                   timedelta(milliseconds=db.running_time_ms(i)))
    return formatted_string



if __name__ == '__main__':
    app.run(debug=True)