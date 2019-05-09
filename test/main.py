import json
from flask import Flask, redirect
from oauth import OAuthSession
from mongoAccess import FitnessDatabase
from datetime import timedelta

ssss = {"web": {
    "client_id": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "authorize_url": "https://accounts.google.com/o/oauth2/auth",
    "access_token_url": "https://oauth2.googleapis.com/token",
    "client_secret": "XXXXXXXXXXXXXXXXXX"
},
    "unused": {
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": ["http://localhost:5000"],
        "javascript_origins": ["http://localhost:5000"]
    }
}
app = Flask(__name__)
app.config['OAUTH_CREDENTIALS'] = ssss['web']
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