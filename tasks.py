import json
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
import own_classes
from own_classes import ImageButton
from functools import partial
import constants
from kivy.network.urlrequest import UrlRequest



class Task:
    operating_task = ''
    task_sort = None


exist_task_url = 'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks/%s.json?auth=%s'


def save_new_task(text):
    app = App.get_running_app()
    if text:
        task_data_for_load = {'description': text, 'status': 'active'}
        if Task.operating_task == '':
        # requests.post присваивает запросу ключ
            try:
                requests.post(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks.json?auth=%s'
                    % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps(task_data_for_load))
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return
        # если task уже существует, то меняем
        else:
            try:
                requests.patch(exist_task_url
                    % (constants.LOCAL_ID, Task.operating_task, constants.ID_TOKEN), data=json.dumps(task_data_for_load))
                Task.operating_task = ''
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return
        refill_tasks_layouts(sort=Task.task_sort)


# заполняет экран заданий
def tasks_fill(data, sort):
    app = App.get_running_app()
    tasks_box_layout = app.root.ids['todolist_screen'].ids['tasks_layout']
    # Проверка на наличие заданий
    if 'tasks' in data:
        # словарь словарей
        tasks = data['tasks']
        # ключи событий
        tasks_keys = tasks.keys()
        # Сортировка заданий
        tasks_list = []
        # добавляем в словарь второго порядка поле с ключами
        for task_key in tasks_keys:
            tasks[task_key]['task_key'] = str(task_key)
            tasks_list.append(tasks[task_key])
        tasks_list = sorted(tasks_list, key=lambda x: (x['status'], ''),
                            reverse=False)
        # Заполнение
        active = 0
        for task in tasks_list:
            layout_for_task = own_classes.NewFloatLayout()
            # добавляем в активные или не активные события
            if task['status'] == 'active':
                active += 1
                description = own_classes.LabelButton(text=task['description'], size_hint=(.7, .8),
                                pos_hint={"top": .87, "right": .75}, halign="left", valign="top", font_size=42)
                description_callback = partial(edit_task, task['task_key'])
                description.bind(size=description.setter('text_size'), on_release=description_callback)

                checkbox = CheckBox(size_hint=(.25, .3), active=False,
                                          pos_hint={"top": .95, "right": 1})
                checkbox_callback = partial(checkbox_active, arg=task['task_key'])
                checkbox.bind(active=checkbox_callback)

                copy_button = ImageButton(source="icons/events/copy.png", size_hint=(.25, .3),
                                          pos_hint={"top": .65, "right": 1})
                but_copy_callback = partial(copy_task, task['task_key'])
                copy_button.bind(on_release=but_copy_callback)

                delete_button = ImageButton(source="icons/events/delete.png", size_hint=(.25, .3),
                                            pos_hint={"top": .35, "right": 1})
                but_delete_callback = partial(delete_task, task['task_key'])
                delete_button.bind(on_release=but_delete_callback)

                layout_for_task.add_widget(description)
                layout_for_task.add_widget(copy_button)
                layout_for_task.add_widget(checkbox)
                layout_for_task.add_widget(delete_button)
                tasks_box_layout.add_widget(layout_for_task)
            elif task['status'] == 'inactive' and sort is None:
                description = Label(markup=True, text=f"[s]{task['description']}[/s]", size_hint=(.7, .8),
                                pos_hint={"top": .87, "right": .75}, halign="left", valign="top", font_size=42)
                description.bind(size=description.setter('text_size'))

                checkbox = CheckBox(size_hint=(.25, .3), active=True,
                                    pos_hint={"top": .95, "right": 1})
                checkbox_callback = partial(checkbox_active, arg=task['task_key'])
                checkbox.bind(active=checkbox_callback)

                copy_button = ImageButton(source="icons/events/copy.png", size_hint=(.25, .3),
                                          pos_hint={"top": .65, "right": 1})
                but_copy_callback = partial(copy_task, task['task_key'])
                copy_button.bind(on_release=but_copy_callback)

                delete_button = ImageButton(source="icons/events/delete.png", size_hint=(.25, .3),
                                            pos_hint={"top": .35, "right": 1})
                but_delete_callback = partial(delete_task, task['task_key'])
                delete_button.bind(on_release=but_delete_callback)

                layout_for_task.add_widget(description)
                layout_for_task.add_widget(checkbox)
                layout_for_task.add_widget(copy_button)
                layout_for_task.add_widget(delete_button)
                tasks_box_layout.add_widget(layout_for_task)

        # Если нет активных заданий в списке
        if active == 0 and sort == 'Actual':
            l = Label(text='You have no scheduled tasks', font_size='20sp', color=(.6, .6, .6, 1),
                      font_name=constants.main_font)
            tasks_box_layout.add_widget(l)
    # Нет никаких заданий в списке
    else:
        l = Label(text='You have no any tasks', font_size='20sp', color=(.6, .6, .6, 1),
                  font_name=constants.main_font)
        tasks_box_layout.add_widget(l)


def edit_task(*args):
    app = App.get_running_app()
    for arg in args:
        if arg.__class__ != own_classes.LabelButton:
            try:
                edit_task_request = requests.get(exist_task_url
                    % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
                Task.operating_task = arg
                modal_edit_task_window(command='edit', task_request=edit_task_request, text='Edit task')
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return


def copy_task(*args):
    for arg in args:
        if arg.__class__ != ImageButton:
            try:
                copy_task_request = requests.get(exist_task_url
                    % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
                modal_edit_task_window(command='copy', task_request=copy_task_request, text='Copy task')
            except Exception:
                app = App.get_running_app()
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return


def checkbox_active(checkbox, value, arg):
    if value:
        try:
            requests.patch(exist_task_url
                % (constants.LOCAL_ID, arg, constants.ID_TOKEN),
                data=json.dumps({'status': 'inactive'}))
        except Exception:
            app = App.get_running_app()
            app.error_modal_screen(text_error=constants.connection_error_msg)
            return
    else:
        try:
            requests.patch(exist_task_url
                % (constants.LOCAL_ID, arg, constants.ID_TOKEN),
                data=json.dumps({'status': 'active'}))
        except Exception:
            app = App.get_running_app()
            app.error_modal_screen(text_error=constants.connection_error_msg)
            return
    refill_tasks_layouts(sort=Task.task_sort)


def delete_task(*args):
    for arg in args:
        if arg.__class__ != ImageButton:
            try:
                get_task_request = requests.get(exist_task_url
                    % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
                Task.operating_task = arg
                modal_edit_task_window(command='delete', task_request=get_task_request, text='Delete this task?')
            except Exception:
                app = App.get_running_app()
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return


def delete_all_completed_tasks(*args):
    try:
        result = requests.get(
            'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
        data = json.loads(result.content.decode())
        inactive_tasks = set()
        if 'tasks' in data:
            # словарь словарей
            tasks = data['tasks']
            # ключи словаря - идентификаторы в базе
            task_keys = tasks.keys()
            # проходим по значениям через ключи словаря
            for task_key in task_keys:
                if tasks[task_key]['status'] == 'inactive':
                    inactive_tasks.add(task_key)

        if inactive_tasks:
            modal_task_window(name='Delete all inactive tasks!!!', label='Delete all completed tasks?',
                              amount=inactive_tasks)

    except Exception:
        app = App.get_running_app()
        app.error_modal_screen(text_error=constants.connection_error_msg)
        return


# перезаполняет layouts с эвентами
def refill_tasks_layouts(sort, data=None):
    app = App.get_running_app()
    tasks_box_layout = app.root.ids['todolist_screen'].ids['tasks_layout']

    def success(request, result):
        for w in tasks_box_layout.walk():
            # Удаляем только FloatLayout
            if w.__class__ == own_classes.NewFloatLayout or w.__class__ == Label or w.__class__ == CheckBox:
                tasks_box_layout.remove_widget(w)
        tasks_fill(sort=sort, data=result)

    def failure(request, error):
        app.error_modal_screen(text_error=constants.connection_error_msg)

    if data == None:
        UrlRequest(
            'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN,
            on_success=success,
            on_failure=failure)
    else:
        success(request=None, result=data)


def modal_edit_task_window(command, task_request, text):
    task_data = json.loads(task_request.content.decode())

    # Создаём модальное окно
    bl = BoxLayout(orientation='vertical')
    t_i = TextInput(text=task_data['description'], size_hint=  (1, .3),
            pos_hint={'top': .85, 'right': 1}, background_color=(0,0,0,1), foreground_color=(1, 1, 1, 1), font_size=40, )
    bl.add_widget(t_i)
    bl2 = BoxLayout(orientation='horizontal')
    but_no = Button(text="Don't save", font_size=40, size_hint=(.3, .4))
    but_yes = Button(text=text, font_size=40, size_hint=(.3, .4))
    bl2.add_widget(but_no)
    bl2.add_widget(but_yes)
    bl.add_widget(bl2)
    popup = Popup(title_align= 'center', title=text, content=bl, size_hint=(1, .45), pos_hint={"x": 0, "top": .78},
                  auto_dismiss=False)

    # если не сохранять
    def no(*args):
        popup.dismiss()

    # чтобы изменить пункт
    def yes(*args):
        popup.dismiss()
        if command == 'edit':
            try:
                requests.patch(exist_task_url
                    % (constants.LOCAL_ID, Task.operating_task, constants.ID_TOKEN),
                    data=json.dumps({'description': t_i.text}))
            except Exception:
                app = App.get_running_app()
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return
        elif command == 'copy':
            try:
                requests.post(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/tasks.json?auth=%s'
                    % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps({'description': t_i.text, 'status': 'active'}))
            except Exception:
                app = App.get_running_app()
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return

        elif command == 'delete':
            try:
                requests.delete(exist_task_url
                    % (constants.LOCAL_ID, Task.operating_task, constants.ID_TOKEN))
            except Exception:
                app = App.get_running_app()
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return

        refill_tasks_layouts(sort=Task.task_sort)
        Task.operating_task = ''

    but_no.bind(on_press=no)
    but_yes.bind(on_press=yes)
    popup.open()


def modal_task_window(name, label, amount=None):
    # Создаём модальное окно
    bl = BoxLayout(orientation='vertical')
    l = Label(text=label, font_size=40, font_name=constants.main_font)
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

    # чтобы перенести в выполненные/удалить
    def yes(*args):
        popup.dismiss()
        for task_key in amount:
            try:
                requests.delete(exist_task_url
                    % (constants.LOCAL_ID, task_key, constants.ID_TOKEN))
            except Exception:
                app = App.get_running_app()
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return
        refill_tasks_layouts(sort=Task.task_sort)

    but_no.bind(on_press=no)
    but_yes.bind(on_press=yes)
    popup.open()