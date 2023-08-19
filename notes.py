import json
from functools import partial
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
import own_classes
from own_classes import ImageButton
import requests
from kivy.app import App
import constants
import tasks
import shopping_list
from kivy.metrics import dp
from kivy.factory import Factory
from kivymd.uix.menu import MDDropdownMenu
from kivy.network.urlrequest import UrlRequest



class Note:
    operating_note = ''


def dropdown_menu(text):
    app = App.get_running_app()
    if text:
        menu_items = [
            {
                "text": "New event",
                "viewclass": "OneLineListItem",
                "height": dp(54),
                "on_release": lambda x='event': transfer_to_event(menu, text)},
            {
                "text": "New To-Do task",
                "viewclass": "OneLineListItem",
                "height": dp(54),
                "on_release": lambda x='todo': transfer_to_todo_list(menu, text)},
            {
                "text": "Add to shoplist",
                "viewclass": "OneLineListItem",
                "height": dp(54),
                "on_release": lambda x='purchase': transfer_to_shopping_list(menu, text)},
            {
                "text": "Add to project",
                # "icon": "icons/plus.png",
                "viewclass": "OneLineListItem",
                "height": dp(54),
                "on_release": lambda x='project': transfer_to_project(menu, text)},
        ]
        menu = MDDropdownMenu(
            caller=app.root.ids["one_note_screen"].ids["transfer"],
            items=menu_items,
            position='auto',
            background_color=(.5, .5, .5, 1),
            width_mult=3,
        )
        menu.open()
    else:
        app.root.ids["one_note_screen"].ids["info_label"].text = 'Your Note is empty'


exist_note_url = 'https://zach-mobile-default-rtdb.firebaseio.com/%s/notes/%s.json?auth=%s'


def transfer_to_project(menu, text):
    menu.dismiss()
    try:
        result = requests.get(
            'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
        data = json.loads(result.content.decode())
        popup_func(data=data, text=text)

    except Exception:
        app = App.get_running_app()
        app.error_modal_screen(text_error=constants.connection_error_msg)
        return


# перекидываем заметку в проект
def one_click_add(key, description_text, adding_text, popup, *args):
    popup.dismiss()
    app = App.get_running_app()
    if key is None:
        app.root.ids["one_project_screen"].ids["description"].text = adding_text
        app.root.ids["one_project_screen"].ids["info_label"].text = ''
        app.change_screen('one_project_screen')
    else:
        new_description_text = f'{description_text} \n {adding_text}'
        try:
            requests.patch(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/projects/%s.json?auth=%s'
                % (constants.LOCAL_ID, key, constants.ID_TOKEN),
                data=json.dumps({'description': new_description_text}))
            app.change_screen(app.previous_screen)
        except Exception:
            app.error_modal_screen(text_error=constants.connection_error_msg)
            return


def popup_func(data, text):
    popup = Factory.NotesToProjPopup()
    # fill the GridLayout
    grid = popup.ids.container2
    but_callback = partial(one_click_add, None, '', text, popup)
    grid.add_widget(Factory.ProjectsButton(text='New project', on_press=but_callback))
    if 'projects' in data:
        projects = data['projects']
        for project in projects:
            if projects[project]['status'] == 'active':
                but_callback = partial(one_click_add, project, projects[project]['description'], text, popup)
                grid.add_widget(Factory.ProjectsButton(text=projects[project]['title'], on_press=but_callback))

    popup.open()


def transfer_to_event(menu, text):
    app = App.get_running_app()
    app.root.ids["new_event_screen"].ids["description"].text = text
    app.change_screen('new_event_screen')
    menu.dismiss()


def transfer_to_todo_list(menu, text):
    app = App.get_running_app()
    tasks.save_new_task(text)
    app.change_screen('notes_screen')
    menu.dismiss()


def transfer_to_shopping_list(menu, text):
    shopping_list.Purchase.operating_purchase = ''
    shopping_list.save_new_purchase(text)
    menu.dismiss()


def save_note():
    app = App.get_running_app()

    description = app.root.ids["one_note_screen"].ids["description"].text
    note_data_for_load = {'description': description}
    if description == '':
        app.root.ids["one_note_screen"].ids["info_label"].text = "Please fill in the description field"
    else:
        if Note.operating_note == '':
            # requests.post присваивает запросу ключ
            try:
                requests.post(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/notes.json?auth=%s'
                    % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps(note_data_for_load))
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return
        else:
            try:
                requests.patch(
                    exist_note_url
                    % (constants.LOCAL_ID, Note.operating_note, constants.ID_TOKEN),
                    data=json.dumps(note_data_for_load))
                Note.operating_note = ''
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return
        clear_one_note_screen()
        app.change_screen("notes_screen")
        refill_notes_screen()


def fill_notes_screen(data):
    app = App.get_running_app()

    notes_layout = app.root.ids['notes_screen'].ids['notes_layout']
    if 'notes' in data:
        notes = data['notes']
        # ключи событий
        notes_keys = notes.keys()
        notes_list = []
        # добавляем в словарь второго порядка поле с ключами
        for note_key in notes_keys:
            notes[note_key]['note_key'] = str(note_key)
            notes_list.append(notes[note_key])
            # Заполнение
        for note in notes_list:
            layout_for_note = own_classes.NewFloatLayout()
            description = own_classes.LabelButton(text=note['description'], size_hint=(.7, .8),
                                pos_hint={"top": .87, "right": .75}, halign="left", valign="top", font_size=42)
            description_callback = partial(edit_note, note['note_key'])
            description.bind(size=description.setter('text_size'), on_release=description_callback)

            delete_button = ImageButton(source="icons/events/delete.png", size_hint=(.25, .4),
                                        pos_hint={"top": .7, "right": 1})
            but_delete_callback = partial(delete_note, note['note_key'])
            delete_button.bind(on_release=but_delete_callback)

            layout_for_note.add_widget(description)
            layout_for_note.add_widget(delete_button)
            notes_layout.add_widget(layout_for_note)
    else:
        l = Label(text='You have not notes', font_size='20sp', color=(.6, .6, .6, 1), font_name='fonts/Nunito-Bold.ttf')
        notes_layout.add_widget(l)


def refill_notes_screen(data=None):
    app = App.get_running_app()
    notes_layout = app.root.ids['notes_screen'].ids['notes_layout']

    def success(request, result):
        for w in notes_layout.walk():
            # Удаляем только FloatLayout
            if w.__class__ == own_classes.NewFloatLayout or w.__class__ == Label:
                notes_layout.remove_widget(w)
        fill_notes_screen(data=result)


    def failure(request, error):
        app.error_modal_screen(text_error=constants.connection_error_msg)

    if data == None:
        UrlRequest(
            'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN,
            on_success=success,
            on_failure=failure)
    else:
        success(request=None, result=data)



def fill_one_note_screen(note_request):
    app = App.get_running_app()

    note_data = json.loads(note_request.content.decode())
    app.previous_screen = 'notes_screen'
    app.root.ids["one_note_screen"].ids["info_label"].text = ''
    app.root.ids["one_note_screen"].ids["description"].text = note_data['description']
    app.change_screen('one_note_screen')


def clear_one_note_screen():
    app = App.get_running_app()
    app.root.ids["one_note_screen"].ids["description"].text = ''
    app.root.ids["one_note_screen"].ids["info_label"].text = ''


def edit_note(*args):
    app = App.get_running_app()
    app.previous_screen = 'notes_screen'
    for arg in args:
        if arg.__class__ != own_classes.LabelButton:
            try:
                edit_note_request = requests.get(
                    exist_note_url
                    % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
                Note.operating_note = arg
                fill_one_note_screen(edit_note_request)
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return


def delete_note(*args):
    app = App.get_running_app()
    app.previous_screen = 'notes_screen'
    for arg in args:
        if arg.__class__ != ImageButton:
            try:
                get_note_request = requests.get(
                    exist_note_url
                    % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
                Note.operating_note = arg
                modal_note_window(name='Delete!', label='Delete this note!?', command='delete')
                fill_one_note_screen(get_note_request)
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return


def modal_note_window(name, label, command):
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
        clear_one_note_screen()
        app.change_screen(app.previous_screen)
        Note.operating_note = ''

    # чтобы перенести в выполненные/удалить
    def yes(*args):
        popup.dismiss()

        if command == 'delete':
            try:
                requests.delete(exist_note_url
                % (constants.LOCAL_ID, Note.operating_note, constants.ID_TOKEN))
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return
        refill_notes_screen()
        clear_one_note_screen()
        app.change_screen(app.previous_screen)
        Note.operating_note = ''

    but_no.bind(on_press=no)
    but_yes.bind(on_press=yes)
    popup.open()
