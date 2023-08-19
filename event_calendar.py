import datetime
import json
import requests
from kivy.app import App
import calendar
from functools import partial
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
import own_classes
from own_classes import ImageButton
import constants
from kivy.uix.screenmanager import Screen
from kivy.network.urlrequest import UrlRequest


class EventCalendarScreen(Screen):
    # days = [] - не понятно зачем надо
    now = datetime.datetime.now()
    year = now.year
    month = now.month


class Event():
    events_list = []
    date_sort = None
    operating_event = ''


exist_event_url = 'https://zach-mobile-default-rtdb.firebaseio.com/%s/events/%s.json?auth=%s'


def start_calendar_fill():
    # EventCalendarScreen.now = datetime.datetime.now()
    # EventCalendarScreen.year = EventCalendarScreen.now.year
    # EventCalendarScreen.month = EventCalendarScreen.now.month

    app = App.get_running_app()
    # инфо табло/calendar.month_name[month] - текущий месяц  + текущий год
    app.root.ids["event_calendar_screen"].ids["month"].text = calendar.month_name[EventCalendarScreen.month] + \
                                                              ', ' + str(EventCalendarScreen.year)

    # calendar.monthrange(year, month)[1] - дней в текущем месяце текущего года
    month_days = calendar.monthrange(EventCalendarScreen.year, EventCalendarScreen.month)[1]
    # если январь
    if EventCalendarScreen.month == 1:
        # дней в декабре прошлого года
        back_month_days = calendar.monthrange(EventCalendarScreen.year - 1, 12)[1]
    else:
        # дней в прошлом месяце текущего года
        back_month_days = calendar.monthrange(EventCalendarScreen.year, EventCalendarScreen.month - 1)[1]
    # первый день месяца (понедельник - 0)
    week_day = calendar.monthrange(EventCalendarScreen.year, EventCalendarScreen.month)[0]

    # n - дни текущего месяца текущего года с 0
    for n in range(month_days):
        # в списке объекту Button по индексам дням присваиваются числа в поле text
        app.root.ids["event_calendar_screen"].ids[str(n + week_day)].text = str(n + 1)
        format_label(day=n + 1, label_day_id=str(n + week_day), direction='ok')

        if EventCalendarScreen.year == EventCalendarScreen.now.year and EventCalendarScreen.month == \
                EventCalendarScreen.now.month and n == EventCalendarScreen.now.day:
            # красим сегодняшний день в зеленый
            app.root.ids["event_calendar_screen"].ids[
                str(EventCalendarScreen.now.day + week_day - 1)].background_color = \
                (38 / 255, 220 / 255, 35 / 255, 1)
            #     # остальные дни - серым
            app.root.ids["event_calendar_screen"].ids[str(n + week_day)].background_color = \
                (115 / 255, 110 / 255, 110 / 255, 1)
        else:
            app.root.ids["event_calendar_screen"].ids[str(n + week_day)].background_color = \
                (115 / 255, 110 / 255, 110 / 255, 1)

    # заполняем дни предыдущего месяца
    for n in range(week_day):
        format_label(day=back_month_days - n, label_day_id=str(week_day - n - 1), direction='back')
        app.root.ids["event_calendar_screen"].ids[str(week_day - n - 1)].text = str(back_month_days - n)
        app.root.ids["event_calendar_screen"].ids[str(week_day - n - 1)].background_color = \
            (31 / 255, 30 / 255, 30 / 255, 1)

    # заполняем дни следующего месяца
    for n in range(6 * 7 - month_days - week_day):
        format_label(day=n + 1, label_day_id=str(week_day + month_days + n), direction='next')
        app.root.ids["event_calendar_screen"].ids[str(week_day + month_days + n)].text = str(n + 1)
        app.root.ids["event_calendar_screen"].ids[str(week_day + month_days + n)].background_color = \
            (31 / 255, 30 / 255, 30 / 255, 1)


# Заполняем лэйбы с эвентами
def format_label(day, label_day_id, direction):
    app = App.get_running_app()
    day_events = 0
    current_month = EventCalendarScreen.month
    label_id = app.root.ids["event_calendar_screen"].ids[label_day_id + 'l']
    if direction == 'next':
        if EventCalendarScreen.month == 12:
            current_month = 1
        else:
            current_month = EventCalendarScreen.month + 1
    elif direction == 'back':
        if EventCalendarScreen.month == 0:
            current_month = 12
        else:
            current_month = EventCalendarScreen.month - 1
    form_day = formatted_date(current_month, day)
    # Проверка на наличие события
    if Event.events_list:
        for event in Event.events_list:
            if event['date'] == form_day:
                day_events += 1
            # отмечаем на календаре события
            label_id.text = f'{day_events} ev'
            if day_events > 0:
                label_id.background_color = (139/255, 62/255, 3/255, 1)
            else:
                label_id.background_color = (27/255, 100/255, 31/255, 1)
                # 0.42, 0.59, 0.37,
    else:
        label_id.text = f'{day_events} ev'
        label_id.background_color = (0.42, 0.59, 0.37, 1)


def month_back():
    EventCalendarScreen.month -= 1
    if EventCalendarScreen.month == 0:
        EventCalendarScreen.month = 12
        EventCalendarScreen.year -= 1
    start_calendar_fill()


def month_next():
    EventCalendarScreen.month += 1
    if EventCalendarScreen.month == 13:
        EventCalendarScreen.month = 1
        EventCalendarScreen.year += 1
    start_calendar_fill()


def formatted_date(current_month, day):
    # форматируем дату и время
    if len(str(current_month)) < 2:
        formatted_month = '0' + str(current_month)
    else:
        formatted_month = current_month
    if len(str(day)) < 2:
        formatted_day = '0' + str(day)
    else:
        formatted_day = day
    return f"{EventCalendarScreen.year}-{formatted_month}-{formatted_day}"


# после нажатия на дату отправляет на предыдущий экран
def calendar_button_release(day, name):
    app = App.get_running_app()
    current_month = EventCalendarScreen.month
    # дни текущего месяца текущего года
    month_days = calendar.monthrange(EventCalendarScreen.year, EventCalendarScreen.month)[1]
    # первый день месяца (понедельник - 0)
    week_day = calendar.monthrange(EventCalendarScreen.year, EventCalendarScreen.month)[0]
    # если нажал на день предыдущего месяца
    if int(name) < week_day:
        # месяц считается предыдущим
        current_month -= 1
    elif int(name) >= week_day + month_days:
        current_month += 1

    date_in_current_format = formatted_date(current_month, day)

    if app.previous_screen == "new_event_screen":
        # проверяем, чтобы дата была не меньше текущей
        if EventCalendarScreen.year > EventCalendarScreen.now.year:
            # переносит на экран создания нового эвента
            app.change_screen(app.previous_screen)
            # заполняет поле с датой
            app.root.ids["new_event_screen"].ids["chosen_date"].text = date_in_current_format
        elif EventCalendarScreen.year >= EventCalendarScreen.now.year and current_month > \
                EventCalendarScreen.now.month:
            app.change_screen(app.previous_screen)
            app.root.ids["new_event_screen"].ids["chosen_date"].text = date_in_current_format
        elif EventCalendarScreen.year >= EventCalendarScreen.now.year and current_month >= \
                EventCalendarScreen.now.month and int(day) >= EventCalendarScreen.now.day:
            app.change_screen(app.previous_screen)
            app.root.ids["new_event_screen"].ids["chosen_date"].text = date_in_current_format
    # Отбираем события по дате
    else:
        Event.date_sort = date_in_current_format
        # лепит автоматом в новый эвент дату из сортировки
        app.root.ids["new_event_screen"].ids["chosen_date"].text = date_in_current_format
        app.root.ids["events_screen"].ids["sort_by_date"].text = Event.date_sort
        app.root.ids["events_screen"].ids["sort_clear_button"].source = "icons/events/s_b_d_unselect.png"
        app.root.ids["inactive_events_screen"].ids["inactive_sort_by_date"].text = Event.date_sort
        app.root.ids["inactive_events_screen"].ids["sort_clear_button"].source = "icons/events/s_b_d_unselect.png"
        refill_events_layouts(sort=Event.date_sort)
        app.change_screen('events_screen')


# заполняет экран эвентов
def events_fill(data, sort):
    app = App.get_running_app()
    # BoxLayout в events_screen
    events_box_layout = app.root.ids['events_screen'].ids['events_layout']
    inactive_events_box_layout = app.root.ids['inactive_events_screen'].ids['inactive_events_layout']
    # Проверка на наличие события
    if 'events' in data:
        events = data['events']
        # ключи событий
        events_keys = events.keys()

        # Сортировка событий
        events_list = []
        # добавляем в словарь второго порядка поле с ключами
        for event_key in events_keys:
            events[event_key]['event_key'] = str(event_key)
            events_list.append(events[event_key])
        events_list = sorted(events_list,
                             key=lambda x: datetime.datetime.strptime(x['date_time'], '%Y-%m-%d %H:%M:%S'),
                             reverse=False)
        Event.events_list = events_list
        # Заполнение
        active = 0
        inactive = 0
        for event in events_list:
            if sort is None or sort == event['date']:
                layout_for_event = own_classes.NewFloatLayout()

                # добавляем в активные или не активные события
                if event['status'] == 'active':
                    active += 1
                    title = own_classes.LabelButton(text=event['title'], size_hint=(.7, .25),
                                                    pos_hint={"top": .95, "right": .75}, color=(.72, .39, 0, 1), halign="left", valign="top",
                                                    font_size=35)
                    title_callback = partial(edit_event, event['event_key'])
                    title.bind(size=title.setter('text_size'), on_release=title_callback)

                    description = own_classes.LabelButton(text=event['description'], size_hint=(.7, .6),
                                        pos_hint={"top": .7, "right": .75}, halign="left", valign="top", font_size=33)
                    description_callback = partial(edit_event, event['event_key'])
                    description.bind(size=description.setter('text_size'), on_release=description_callback)


                    date = Label(text=event['date'], size_hint=(.4, .3), color=(.6, .6, .6, 1),
                                 pos_hint={"top": .3, "left": .5}, font_name=constants.main_font)
                    time = Label(text=event['time'], size_hint=(.4, .3), color=(.6, .6, .6, 1),
                                 pos_hint={"top": .3, "right": .8}, font_name=constants.main_font)

                    copy_button = ImageButton(source="icons/events/copy.png", size_hint=(.25, .3),
                                              pos_hint={"top": .95, "right": 1})
                    but_copy_callback = partial(copy_event, event['event_key'])
                    copy_button.bind(on_release=but_copy_callback)

                    done_button = ImageButton(source="icons/events/done.png", size_hint=(.25, .3),
                                              pos_hint={"top": .65, "right": 1})
                    but_done_callback = partial(done_event, event['event_key'])
                    done_button.bind(on_release=but_done_callback)

                    delete_button = ImageButton(source="icons/events/delete.png", size_hint=(.25, .3),
                                                pos_hint={"top": .35, "right": 1})
                    but_delete_callback = partial(delete_event, event['event_key'])
                    delete_button.bind(on_release=but_delete_callback)

                    layout_for_event.add_widget(title)
                    layout_for_event.add_widget(description)
                    layout_for_event.add_widget(date)
                    layout_for_event.add_widget(time)
                    layout_for_event.add_widget(copy_button)
                    layout_for_event.add_widget(done_button)
                    layout_for_event.add_widget(delete_button)
                    events_box_layout.add_widget(layout_for_event)
                elif event['status'] == 'inactive':
                    inactive += 1
                    title = Label(text=event['title'], size_hint=(.7, .25),
                                pos_hint={"top": .95, "right": .75}, color=(.72, .39, 0, 1), halign="left", valign="top",
                                  font_size=35)
                    title.bind(size=title.setter('text_size'))

                    description = Label(text=event['description'], size_hint=(.7, .6),
                                        pos_hint={"top": .7, "right": .75}, halign="left", valign="top", font_size=33)
                    description.bind(size=description.setter('text_size'))

                    date = Label(text=event['date'], size_hint=(.4, .3), color=(.6, .6, .6, 1),
                                 pos_hint={"top": .3, "left": .5}, font_name=constants.main_font)
                    time = Label(text=event['time'], size_hint=(.4, .3), color=(.6, .6, .6, 1),
                                 pos_hint={"top": .3, "right": .8, }, font_name=constants.main_font)

                    copy_button = ImageButton(source="icons/events/copy.png",  size_hint=(.25, .3),
                                              pos_hint={"top": .9, "right": 1})
                    but_copy_callback = partial(copy_event, event['event_key'])
                    copy_button.bind(on_release=but_copy_callback)

                    delete_button = ImageButton(source="icons/events/delete.png", size_hint=(.25, .3),
                                                pos_hint={"top": .4, "right": 1})
                    but_delete_callback = partial(delete_event, event['event_key'])
                    delete_button.bind(on_release=but_delete_callback)
                    layout_for_event.add_widget(title)
                    layout_for_event.add_widget(description)
                    layout_for_event.add_widget(date)
                    layout_for_event.add_widget(time)
                    layout_for_event.add_widget(copy_button)
                    layout_for_event.add_widget(delete_button)
                    inactive_events_box_layout.add_widget(layout_for_event)

        # Если нет эвентов в списке
        if active == 0:
            l = Label(text='You have no scheduled events', font_size='20sp', color=(.6, .6, .6, 1), font_name=constants.main_font)
            events_box_layout.add_widget(l)
        if inactive == 0:
            l = Label(text='You have no completed events', font_size='20sp', color=(.6, .6, .6, 1), font_name=constants.main_font)
            inactive_events_box_layout.add_widget(l)
    else:
        l = Label(text='You have no scheduled events', font_size='20sp',  color=(.6, .6, .6, 1), font_name=constants.main_font)
        events_box_layout.add_widget(l)
        l = Label(text='You have no completed events', font_size='20sp',  color=(.6, .6, .6, 1), font_name=constants.main_font)
        inactive_events_box_layout.add_widget(l)
        Event.events_list = []
    # заполняем календарь
    EventCalendarScreen.now = datetime.datetime.now()
    EventCalendarScreen.year = EventCalendarScreen.now.year
    EventCalendarScreen.month = EventCalendarScreen.now.month
    start_calendar_fill()


# перезаполняет layouts с эвентами
def refill_events_layouts(sort, data=None):
    app = App.get_running_app()
    events_box_layout = app.root.ids['events_screen'].ids['events_layout']
    inactive_events_box_layout = app.root.ids['inactive_events_screen'].ids['inactive_events_layout']

    def success(request, result):
        for w in events_box_layout.walk():
            # Удаляем только FloatLayout
            if w.__class__ == own_classes.NewFloatLayout or w.__class__ == Label:
                events_box_layout.remove_widget(w)
        for w in inactive_events_box_layout.walk():
            if w.__class__ == own_classes.NewFloatLayout or w.__class__ == Label:
                inactive_events_box_layout.remove_widget(w)
        events_fill(sort=sort, data=result)


    def failure(request, error):
        app.error_modal_screen(text_error=constants.connection_error_msg)

    if data == None:
        UrlRequest(
            'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN,
            on_success=success,
            on_failure=failure)
    else:
        success(request=None, result=data)


def save_new_event():
    app = App.get_running_app()
    title = app.root.ids["new_event_screen"].ids["title"].text
    description = app.root.ids["new_event_screen"].ids["description"].text
    time = app.root.ids["new_event_screen"].ids["chosen_time"].text
    date = app.root.ids["new_event_screen"].ids["chosen_date"].text
    date_time = f"{date} {time}"
    # проверяем заполнение полей
    if title == '':
        app.root.ids["new_event_screen"].ids["info_label"].text = "Please fill in the title field"
    elif description == '':
        app.root.ids["new_event_screen"].ids["info_label"].text = "Please fill in the description field"
    elif date == 'date':
        app.root.ids["new_event_screen"].ids["info_label"].text = "Please chose the date"
    elif time == 'time':
        app.root.ids["new_event_screen"].ids["info_label"].text = "Please chose the time"
    else:
        # Отправляем данные в firebase

        event_data_for_load = {'title': title, 'description': description, 'time': time, 'date': date,
                               'status': 'active', 'date_time': date_time}
        if Event.operating_event == '':
            # requests.post присваивает запросу ключ
            try:
                requests.post(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/events.json?auth=%s'
                    % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps(event_data_for_load))
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return

        # если эвент уже существует, то меняем
        else:
            try:
                requests.patch(
                    exist_event_url
                    % (constants.LOCAL_ID, Event.operating_event, constants.ID_TOKEN), data=json.dumps(event_data_for_load))
                Event.operating_event = ''
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return

        clear_new_event_screen()
        app.change_screen("events_screen")
        refill_events_layouts(sort=Event.date_sort)


def clear_new_event_screen():
    app = App.get_running_app()
    app.root.ids["new_event_screen"].ids["info_label"].text = ''
    app.root.ids["new_event_screen"].ids["title"].text = ''
    app.root.ids["new_event_screen"].ids["description"].text = ''
    app.root.ids["new_event_screen"].ids["chosen_time"].text = 'time'
    app.root.ids["new_event_screen"].ids["chosen_date"].text = 'date'


def edit_event(*args):
    app = App.get_running_app()
    app.previous_screen = 'events_screen'
    for arg in args:
        if arg.__class__ != own_classes.LabelButton:
            try:
                edit_event_request = requests.get(
                    exist_event_url
                    % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
                Event.operating_event = arg
                fill_new_event_screen(edit_event_request)
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)


def done_event(*args):
    app = App.get_running_app()
    app.previous_screen = 'events_screen'
    for arg in args:
        if arg.__class__ != ImageButton:
            try:
                done_event_request = requests.get(
                    exist_event_url
                    % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
                Event.operating_event = arg
                modal_event_window(name='Done!', label="It's finished?", command='patch')
                fill_new_event_screen(done_event_request)
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)


def delete_event(*args):
    app = App.get_running_app()
    app.previous_screen = 'events_screen'
    for arg in args:
        if arg.__class__ != ImageButton:
            try:
                get_event_request = requests.get(
                    exist_event_url
                    % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
                Event.operating_event = arg
                modal_event_window(name='Delete!', label='Delete event!?', command='delete')
                fill_new_event_screen(get_event_request)
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)


def copy_event(*args):
    app = App.get_running_app()
    app.previous_screen = 'events_screen'
    for arg in args:
        if arg.__class__ != ImageButton:
            try:
                copy_event_request = requests.get(
                    exist_event_url
                    % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
                fill_new_event_screen(copy_event_request)
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)


def fill_new_event_screen(event_request):
    app = App.get_running_app()
    event_data = json.loads(event_request.content.decode())
    if event_data['status'] == 'inactive':
        app.previous_screen = 'inactive_events_screen'
    else:
        app.previous_screen = 'events_screen'
    app.root.ids["new_event_screen"].ids["info_label"].text = ''
    app.root.ids["new_event_screen"].ids["title"].text = event_data['title']
    app.root.ids["new_event_screen"].ids["description"].text = event_data['description']
    app.root.ids["new_event_screen"].ids["chosen_time"].text = event_data['time']
    app.root.ids["new_event_screen"].ids["chosen_date"].text = event_data['date']
    app.change_screen('new_event_screen')


def modal_event_window(name, label, command):
    app = App.get_running_app()
    # Создаём модальное окно
    bl = BoxLayout(orientation='vertical')
    l = Label(text=label, font_size=40, font_name='fonts/Nunito-Bold.ttf')
    bl.add_widget(l)
    bl2 = BoxLayout(orientation='horizontal')
    but_no = Button(text='No', font_size=40, size_hint=(.3, .4))
    but_yes = Button(text='Yes', font_size=40, size_hint=(.3, .4))
    bl2.add_widget(but_no)
    bl2.add_widget(but_yes)
    bl.add_widget(bl2)
    popup = Popup(title_align= 'center', title=name, content=bl, size_hint=(1, .45), pos_hint={"x": 0, "top": .78},
                  auto_dismiss=False)

    # усли не будешь менять статус
    def no(*args):
        popup.dismiss()
        app.change_screen(app.previous_screen)
        clear_new_event_screen()
        Event.operating_event = ''

    # чтобы перенести в выполненные/удалить
    def yes(*args):
        popup.dismiss()
        if command == 'patch':
            try:
                requests.patch(
                    exist_event_url
                    % (constants.LOCAL_ID, Event.operating_event, constants.ID_TOKEN), data=json.dumps({'status': 'inactive'}))
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return
        elif command == 'delete':
            try:
                requests.delete(
                    exist_event_url
                    % (constants.LOCAL_ID, Event.operating_event, constants.ID_TOKEN), data=json.dumps({'status': 'inactive'}))
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return
        refill_events_layouts(sort=Event.date_sort)
        app.change_screen(app.previous_screen)
        clear_new_event_screen()
        Event.operating_event = ''

    but_no.bind(on_press=no)
    but_yes.bind(on_press=yes)
    popup.open()