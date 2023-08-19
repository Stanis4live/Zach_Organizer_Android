import random

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from my_base import MyBase
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, NoTransition, CardTransition
import tasks
import event_calendar
import shopping_list
import projects
import notes
import settings
import constants
import datetime
import requests
import json
import my_base as mb
from own_classes import KV
from kivy.network.urlrequest import UrlRequest


class EventCalendarScreen(Screen):
    days = []
    now = datetime.datetime.now()
    year = now.year
    month = now.month


class NewEventScreen(Screen):
    pass


class InactiveEventsScreen(Screen):
    pass


class HomeScreen(Screen):
    pass


class CalendarScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class EventsScreen(Screen):
    pass


class TodolistScreen(Screen):
    pass


class ProjectsScreen(Screen):
    pass


class ArchiveProjectsScreen(Screen):
    pass


class OneProjectScreen(Screen):
    pass


class SupplementScreen(Screen):
    pass


class LoginScreen(Screen):
    pass


class ShoppingListScreen(Screen):
    pass


class NotesScreen(Screen):
    pass


class OneNoteScreen(Screen):
    pass


class LoginRecoveryScreen(Screen):
    pass


class VerificationScreen(Screen):
    pass


class SupportMessageScreen(Screen):
    pass


class SignUpScreen(Screen):
    pass


class TimeScreen(Screen):
    pass

ver_file = 'verification.txt'



from kivy.utils import get_color_from_hex


class MainApp(MDApp):
    lock = 1
    previous_screen = 'home_screen'

    def verification_restart_app(self):
        self.on_start()


    def build(self):
        self.theme_cls.theme_style = 'Light'
        self.theme_cls.primary_palette = 'BlueGray'
        self.theme_cls.colors.update({
            "my_palette": (
                get_color_from_hex("#000080"),  # Primary
                get_color_from_hex("#00FF00"),  # -------------
                get_color_from_hex("#FFFFFF"),  # Light
                get_color_from_hex("#000000"),  # Dark
                get_color_from_hex("#FF0000"),  # Accent
            )
        })
        self.my_base = MyBase()
        Builder.load_string(KV)

    def on_start(self):
        # Делаем запрос для первого заполнения
        def success(request, result):
            # Если даёт ответ, но база данных пустая
            if result is None:
                data = {"user_telephone": "", "user_name": "", "user_lname": "", "user_email": mb.user_email,
                        'sms_remind': False, 'email_remind': False, 'timezone': ''}
                self.lock = 0
                self.my_data = json.dumps(data)
                # Заполняем базу данных
                self.my_base.create_user(my_data=self.my_data, idToken=constants.ID_TOKEN,
                                         localId=constants.LOCAL_ID)
                # Получаем данные обычным реквестом и заполняем
                result = requests.get(
                    'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
                self.first_fill(request=None, result=result)
                # создаём файл верификации
                with open(ver_file, 'w') as f:
                    f.write('Verification : True')
            else:
                # Если всё норм и база не пустая, то заполняем
                self.first_fill(request=request, result=result)
                with open(ver_file, 'w') as f:
                    f.write('Verification : True')


        def failure(request, error):
            # Если не даёт доступ к БД, пусть активирует имейл
            if request.resp_status == 401:
                self.change_screen('verification_screen')
            else:
                # Если не норм и ошибка любая другая, то исключение
                raise ValueError("Ошибка доступа к базе данных")

        # Пытаемся найти файл с верификацией (для повторных входов)
        try:
            with open(ver_file, 'r') as v:
                v.read()
                mb.exchange_refresh_token(lambda: UrlRequest(
                    'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN,
                    on_success=success,
                    on_failure=failure))
                # Если файл открылся, пробуем получить данные с сервера
        # Попали на исключение, если не открылся файл или ошибка сервера кроме 401
        # Если не находим, то возвращаемся на экран верификации
        except Exception:
            try:
                # Он исключения сам обрабатывает
                mb.exchange_refresh_token(lambda: UrlRequest(
                    'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN,
                    on_success=success,
                    on_failure=failure))
            except Exception:
                pass


    def first_fill(self, request, result):
        # заполняем всю херню
        try:
            # и переходим на Home screen
            self.root.ids['screen_manager'].transition = NoTransition()
            self.change_screen('home_screen')
            self.root.ids['screen_manager'].transition = CardTransition()
            self.lock = 0
            settings.user_settings_fill(data=result)
            event_calendar.refill_events_layouts(sort=None, data=result)
            shopping_list.refill_shopping_list_layout(data=result)
            tasks.refill_tasks_layouts(sort=tasks.Task.task_sort, data=result)
            notes.refill_notes_screen(data=result)
            projects.refill_projects_screen(data=result)

        except Exception:
            pass


    def change_screen(self, screen_name):
        screen_manager = self.root.ids["screen_manager"]
        screen_manager.current = screen_name

    def error_modal_screen(self, text_error):
        message = random.randint(0, len(constants.messages_list)-1)
        # Создаём модальное окно
        bl = BoxLayout(orientation='vertical')
        l = Label(text=constants.messages_list[message], font_size=30)
        bl.add_widget(l)
        bl2 = BoxLayout(orientation='horizontal')
        but_restart = Button(text='Continue', font_size=40, size_hint=(.3, .5))
        bl2.add_widget(but_restart)
        bl.add_widget(bl2)
        popup = Popup(title_align= 'center', title="The app was in sleep mode", content=bl, size_hint=(1, .45), pos_hint={"x": 0, "top": .78},
                      auto_dismiss=False)

        def try_again(*args):
            mb.exchange_refresh_token(lambda: popup.dismiss())


        but_restart.bind(on_press=try_again)
        popup.open()

    # Разблокирует home and settings, когда залогинился
    def unlock_header(self, command):
        if not self.lock:
            if command == 'home':
                self.change_screen('home_screen')
                self.previous_screen = 'home_screen'
            elif command == 'settings':
                self.change_screen('settings_screen')



MainApp().run()
