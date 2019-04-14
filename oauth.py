import json
from uuid import uuid4
from rauth import OAuth2Service
from flask import current_app, url_for, request, redirect, session


class OAuthSession(object):

    def __init__(self):
        self.credentials = current_app.config['OAUTH_CREDENTIALS']
        self.service = OAuth2Service(
            **self.credentials
        )


    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))
        self.session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': OAuthSession.get_callback_url()},
            decoder=decode_json
        )

    @staticmethod
    def authorize():
        session = OAuthSession()
        return redirect(session.service.get_authorize_url(
            scope='email ' +
                  'profile ' +
                  'openid ' +
                  'https://www.googleapis.com/auth/fitness.activity.read ' +
                  'https://www.googleapis.com/auth/fitness.body.read ' +
                  'https://www.googleapis.com/auth/fitness.location.read',
            response_type='code',
            redirect_uri=OAuthSession.get_callback_url())
        )


    def get(self,request):
        return self.session.get(request).json()

    def post(self,request,data):
        return self.session.post(request, json=data).json()

    @staticmethod
    def get_callback_url():
        # return url_for('auth_success',
        #                _external=True)# заменить этим кодом при переносе на актуальный домен
        return "http://lvh.me:5000/auth_success"

