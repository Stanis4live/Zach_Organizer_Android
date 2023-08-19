import os
import requests
import json
from kivy.app import App
import constants
import pyrebase
from configuration import WAK, CONFIG
from kivy.network.urlrequest import UrlRequest


firebaseConfig = CONFIG

firebase = pyrebase.initialize_app(firebaseConfig)

auth = firebase.auth()
db = firebase.database()
token_file = 'refresh_token.txt'

user_email = ''


def logout():
    app = App.get_running_app()
    path_rfr = token_file
    path_vrf = 'verification.txt'
    app.lock = 1
    if os.path.isfile(path_rfr):
        os.remove(path_rfr)
        constants.LOCAL_ID = None
        constants.ID_TOKEN = None
    if os.path.isfile(path_vrf):
        os.remove(path_vrf)
    app.root.ids['login_screen'].ids['login_button'].source = "icons/login/login_white.png"
    app.root.ids['login_screen'].ids['forgot_button'].source = "icons/login/forgot_white.png"
    app.root.ids['login_screen'].ids['sign_up_button'].source = "icons/login/sign_up_white.png"
    app.root.ids['sign_up_screen'].ids['sign_up_button'].source = "icons/login/sign_up_white.png"
    app.root.ids['login_recovery_screen'].ids['refresh_button'].source = "icons/login/refresh_white.png"
    app.change_screen('login_screen')


def exchange_refresh_token(on_success_func):
    app = App.get_running_app()

    def success(req, result):
        constants.LOCAL_ID = result['user_id']
        constants.ID_TOKEN = result['id_token']
        if on_success_func:
            on_success_func()

    def failure(req, error):
        app.change_screen('login_screen')
        if isinstance(error, requests.exceptions.ConnectionError):
            app.error_modal_screen(text_error=constants.connection_error_msg)
        else:
            app.root.ids['login_screen'].ids['login_message'].text = 'Please enter your email and password'

    try:
        with open(token_file, 'r') as f:
            refresh_token = f.read()
        refresh_url = 'https://securetoken.googleapis.com/v1/token?key=' + WAK
        refresh_payload = "{'grant_type': 'refresh_token', 'refresh_token': '%s'}" % refresh_token
        UrlRequest(refresh_url, on_success=success, on_failure=failure, req_body=refresh_payload)
    except Exception:
        app.change_screen('login_screen')
        app.root.ids['login_screen'].ids['login_message'].text = 'Please enter your email and password'


def verification_request(id_token):
    payload = json.dumps({
        "requestType": "VERIFY_EMAIL",
        "idToken": id_token
    })
    requests.post("https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode",
                      params={"key": WAK},
                      data=payload)


def password_visibility(state, action):
    app = App.get_running_app()
    if action == 'login':
        if state:
            app.root.ids['login_screen'].ids['login_password'].password = False
        else:
            app.root.ids['login_screen'].ids['login_password'].password = True
    else:
        if state:
            app.root.ids['sign_up_screen'].ids['sign_up_password'].password = False
            app.root.ids['sign_up_screen'].ids['confirm_password'].password = False
        else:
            app.root.ids['sign_up_screen'].ids['sign_up_password'].password = True
            app.root.ids['sign_up_screen'].ids['confirm_password'].password = True


class MyBase:
    # При нажатии на кнопку Sign up
    def sign_up(self, email, password, confirm_password):
        app = App.get_running_app()
        if password == confirm_password:
            global user_email
            user_email = email
            signup_url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=" + WAK

            signup_payload = {"email": email, "password": password, "returnSecureToken": True}

            try:
                # Передаём в базу имейл и пассворд
                sign_up_request = requests.post(signup_url, data=signup_payload)
                sign_up_data = json.loads(sign_up_request.content.decode())

                if sign_up_request.ok:
                    verification_request(id_token=sign_up_data['idToken'])
                    refresh_token = sign_up_data['refreshToken']
                    self.localId = sign_up_data['localId']
                    self.idToken = sign_up_data['idToken']  # authToken

                    with open(token_file, 'w') as f:
                        f.write(refresh_token)
                        app.change_screen('verification_screen')
              # показываем текст ошибки в лэйбле, если данные введены неверно
                if not sign_up_request.ok:
                    error_data = json.loads(sign_up_request.content.decode())
                    error_message = error_data['error']['message']
                    app.root.ids['sign_up_screen'].ids['sign_up_message'].text = error_message
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
        else:
            app.root.ids['sign_up_screen'].ids['sign_up_message'].text = \
                "password and password confirmation don't match"


    # Вызывается с панели Login screen
    def login(self, email, password):
        app = App.get_running_app()
        global user_email
        user_email = email
        try:
            login = auth.sign_in_with_email_and_password(email, password)
            refresh_token = login['refreshToken']
            localId = login['localId']
            idToken = login['idToken']  # authToken
            with open(token_file, 'w') as f:
                f.write(refresh_token)
            constants.LOCAL_ID = localId  # uid
            constants.ID_TOKEN = idToken
            app.on_start()
        except Exception as ex:
            try:
                error_dict = json.loads(ex.args[1])
                app.root.ids['login_screen'].ids['login_message'].text = error_dict['error']['message']
            except Exception:
                error_dict = ex
                app.root.ids['login_screen'].ids['login_message'].text = constants.connection_error_msg


    def create_user(self, idToken, my_data, localId):
        app = App.get_running_app()
        try:
            requests.patch("https://zach-mobile-default-rtdb.firebaseio.com/" + localId + ".json?auth="
                                          + idToken, data=my_data)
            app.change_screen('home_screen')
        except Exception:
            app.error_modal_screen(text_error=constants.connection_error_msg)






