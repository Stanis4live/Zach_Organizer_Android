import json
import requests
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
import pytz
from functools import partial
from kivy.factory import Factory
import constants
import my_base
from kivy.app import App


wait_message = 'Wait for verification'
setting_url = 'https://zach-mobile-default-rtdb.firebaseio.com/%s.json?auth=%s'
suppurt_url = 'https://zach-mobile-default-rtdb.firebaseio.com/%s/support_req.json?auth=%s'


# Изменить свой пароль
def reset_password(email):
    app = App.get_running_app()
    try:
        my_base.auth.send_password_reset_email(email)
        modal_label_window(name='Change the password',
                           label='A link to change your password has been sent to your email')
        app.change_screen('login_screen')
    except Exception as exc:
        try:
            error_dict = json.loads(exc.args[1])
            app.root.ids['login_recovery_screen'].ids['login_message'].text = error_dict['error']['message']
        except Exception:
            app.error_modal_screen(text_error=constants.connection_error_msg)


def modal_label_window(name, label):
    # Создаём модальное окно
    bl = BoxLayout(orientation='vertical')
    l = Label(text=label, font_size=40, halign="center", valign="middle", font_name=constants.main_font)
    l.bind(size=l.setter('text_size'))
    bl.add_widget(l)
    but_ok = Button(text='Ok', font_size=40, size_hint=(.4, .25), pos_hint={"x": 0.3, "top": .1})
    bl.add_widget(but_ok)
    popup = Popup(title_align= 'center', title=name, content=bl,  size_hint=(1, .45), pos_hint={"x": 0, "top": .78}, )

    # просто закрываем модальное окно
    def ok(*args):
        popup.dismiss()

    but_ok.bind(on_press=ok)
    popup.open()


def user_settings_fill(data):
    app = App.get_running_app()
    # Заполняем данные пользователя
    app.root.ids['settings_screen'].ids['user_name'].text = data['user_name']
    app.root.ids['settings_screen'].ids['user_lname'].text = data['user_lname']
    app.root.ids['settings_screen'].ids['user_email'].text = data['user_email']
    app.root.ids['settings_screen'].ids['user_telephone'].text = data['user_telephone']
    app.root.ids['settings_screen'].ids['timezone'].text = data['timezone']
    app.root.ids['settings_screen'].ids['sms_reminder'].active = data['sms_remind']
    app.root.ids['settings_screen'].ids['email_reminder'].active = data['email_remind']
    if data['timezone'] == '':
        app.root.ids['settings_screen'].ids['attention'].text = 'To receive reminders, you must fill the timezone field!'
        app.root.ids['settings_screen'].ids['attention'].color = (1, 0, 0, 1)
    elif data['user_telephone'] == wait_message or data['user_telephone'] == '':
        app.root.ids['settings_screen'].ids['attention'].text = 'To receive SMS reminders, you must fill the phone field!'
        app.root.ids['settings_screen'].ids['attention'].color = (1, 0, 0, 1)
    else:
        app.root.ids['settings_screen'].ids['attention'].text = 'All data is filled'
        app.root.ids['settings_screen'].ids['attention'].color = (0, 0.39, 0, 1)


def user_settings_refill():
    app = App.get_running_app()
    try:
        result = requests.get(
            'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
        data = json.loads(result.content.decode())
        settings_layout = app.root.ids['settings_screen']
        for w in settings_layout.walk():
            if w.__class__  == Label:
                settings_layout.remove_widget(w)
        user_settings_fill(data=data)
    except Exception:
        app.error_modal_screen(text_error="Please check your internet connection!)")


def modal_settings_window(command):
    app = App.get_running_app()
    user_settings_refill()
    # если код ещё не отправлен
    if command == 'verification' and app.root.ids['settings_screen'].ids['user_telephone'].text != 'Wait for ' \
                                                                                                   'verification':
        modal_label_window(label='First you need to add your phone number in the appropriate field.',
                           name="You haven't received a code yet.")
        return

    if command == 'user_name':
        hint_text = 'name'
        lavel_text = 'Please enter your name'
        title_text = 'Filling in the name'
    elif command == 'telephone':
        hint_text = 'Including country code (+000000000000)'
        lavel_text = 'Please enter your correct telephone number'
        title_text = 'Filling in the telephone number'
    elif command == 'verification':
        hint_text = 'XXXXXX'
        lavel_text = 'Enter the six-digit verification code from SMS'
        title_text = 'Verify phone number'
    else:
        hint_text = 'last name'
        lavel_text = 'Please enter your last name'
        title_text = 'Filling in the last name'


    # Создаём модальное окно
    bl = BoxLayout(orientation='vertical')
    l = Label(text=lavel_text, font_size=30, font_name=constants.main_font)
    t_i = TextInput(multiline=False, hint_text=hint_text, font_size=30)
    l2 = Label(text='', font_size=30, font_name=constants.main_font)
    bl.add_widget(l)
    bl.add_widget(t_i)
    bl.add_widget(l2)
    bl2 = BoxLayout(orientation='horizontal')
    but_no = Button(text='Cancel', font_size=40, size_hint=(.3, .7))
    but_yes = Button(text='Save', font_size=40, size_hint=(.3, .7))
    bl2.add_widget(but_no)
    bl2.add_widget(but_yes)
    bl.add_widget(bl2)
    popup = Popup(title_align= 'center', title=title_text, content=bl, size_hint=(1, .45), pos_hint={"x": 0, "top": .78},
                  auto_dismiss=False)

    # усли не будешь менять статус
    def no(*args):
        popup.dismiss()

    def yes(*args):
        if command == 'telephone':
            if len(t_i.text) == 13 and t_i.text[0] == '+' and t_i.text[1:].isdigit():
                send_support_req(data=t_i.text, command=command)
                popup.dismiss()
                modal_label_window(label='The verification code will come to your phone within a minute, '
                                         'after that you need to enter it in the appropriate field.',
                                   name='Code coming soon.')
            else:
                l2.text = 'You entered an invalid phone number'
        elif command == 'verification':
            if len(t_i.text) == 6 and t_i.text.isdigit():
                send_support_req(data=t_i.text, command=command)
                modal_label_window(label='Please wait for verification. This may take about an minute.',
                                   name='The code has been sent for verification.')
                popup.dismiss()
            else:
                l2.text = 'Your verification code is incorrect'

        else:
            popup.dismiss()
            try:
                requests.patch(setting_url
                    % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps({command: t_i.text}))
                user_settings_refill()
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return

    but_no.bind(on_press=no)
    but_yes.bind(on_press=yes)
    popup.open()


def popup_func():
    popup = Factory.SettingsPopup()
    # fill the GridLayout
    grid = popup.ids.container1
    time_zones = pytz.all_timezones
    for zone in time_zones:
        but_callback = partial(add_timezone, popup)
        grid.add_widget(Factory.MyButton(text=zone, on_press=but_callback))

    popup.open()


def info_popup():
    bl = BoxLayout(orientation='vertical')
    l = Label(text='Your message has been sent to support', font_size=40, halign="center", valign="middle",
              font_name=constants.main_font)
    l.bind(size=l.setter('text_size'))
    bl.add_widget(l)
    but_ok = Button(text='Ok', font_size=40, size_hint=(.35, .25), pos_hint={"x": 0.35, "top": .1})
    bl.add_widget(but_ok)
    popup = Popup(title_align= 'center', title='Message sent', content=bl, size_hint=(1, .45), pos_hint={"x": 0, "top": .78})

    def ok(*args):
        popup.dismiss()

    but_ok.bind(on_press=ok)
    popup.open()


def add_timezone(popup, butt):
    popup.dismiss()
    try:
        requests.patch(setting_url
            % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps({'timezone': butt.text}))
        user_settings_refill()
    except Exception:
        app = App.get_running_app()
        app.error_modal_screen(text_error=constants.connection_error_msg)
        return


def set_email_reminder(value):
    try:
        requests.patch(setting_url
            % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps({'email_remind': value}))
        user_settings_refill()
    except Exception:
        app = App.get_running_app()
        app.error_modal_screen(text_error=constants.connection_error_msg)
        return


def set_sms_reminder(value):
    app = App.get_running_app()
    if value == True and app.root.ids['settings_screen'].ids['user_telephone'].text == '':
        modal_label_window(label='First you need to add a phone number.', name='Phone number not found!')

        user_settings_refill()

    elif value == True and app.root.ids['settings_screen'].ids['user_telephone'].text == wait_message:
        modal_label_window(label='First you need to add a phone number.', name='Phone number not found!')

        user_settings_refill()

    else:
        try:
            requests.patch(setting_url
                % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps({'sms_remind': value}))
            user_settings_refill()
        except Exception:
            app.error_modal_screen(text_error=constants.connection_error_msg)
            return


def send_support_req(data, command):
    app = App.get_running_app()
    if command == 'telephone':
        try:
            # отправляем запрос на подтверждение номера телефона
            requests.patch(suppurt_url
                % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps({command: data}))
            # в поле с номером телефона пишем ждать
            requests.patch(setting_url
                % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps({'user_telephone': wait_message}))
            user_settings_refill()
        except Exception:
            app.error_modal_screen(text_error=constants.connection_error_msg)

    elif command == 'verification':
        # если отправил код на верификацию
        try:
            requests.patch(suppurt_url
                % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps({command: data}))
        except Exception:
            app.error_modal_screen(text_error=constants.connection_error_msg)

    elif command == 'message':
        if data != '':
            # если написал сообщение в поддержку
            try:
                requests.patch(suppurt_url
                    % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps({command: data}))
                app.change_screen("settings_screen")
                app.root.ids['support_message_screen'].ids['info_label'].text = ''
                app.root.ids['support_message_screen'].ids['message_text'].text = ''
                info_popup()
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
        else:
            app.root.ids['support_message_screen'].ids['info_label'].text = 'Please enter your message'






