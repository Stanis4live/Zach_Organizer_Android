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
from kivy.network.urlrequest import UrlRequest



class Project:
    operating_project = ''


exist_project_url = 'https://zach-mobile-default-rtdb.firebaseio.com/%s/projects/%s.json?auth=%s'


def save_project():
    app = App.get_running_app()

    title = app.root.ids["one_project_screen"].ids["title"].text
    description = app.root.ids["one_project_screen"].ids["description"].text
    project_data_for_load = {'title': title, 'description': description,
                             'status': 'active'}
    if title == '':
        app.root.ids["one_project_screen"].ids["info_label"].text = "Please fill in the title field"
    else:
        if Project.operating_project == '':
            # requests.post присваивает запросу ключ
            requests.post(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/projects.json?auth=%s'
                % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps(project_data_for_load))
            # если эвент уже существует, то меняем

        else:
            requests.patch(exist_project_url
                % (constants.LOCAL_ID, Project.operating_project, constants.ID_TOKEN),
                data=json.dumps(project_data_for_load))
            Project.operating_project = ''
        clear_one_project_screen()
        app.change_screen("projects_screen")
        refill_projects_screen()


def fill_projects_screen(data):
    app = App.get_running_app()

    # GreedLayout в projects_screen
    projects_layout = app.root.ids['projects_screen'].ids['projects_layout']
    archive_projects_layout = app.root.ids['archive_projects_screen'].ids['archive_projects_layout']

    if 'projects' in data:
        projects = data['projects']
        # ключи событий
        projects_keys = projects.keys()
        projects_list = []
        # добавляем в словарь второго порядка поле с ключами
        for project_key in projects_keys:
            projects[project_key]['project_key'] = str(project_key)
            projects_list.append(projects[project_key])
            # Заполнение
            active = 0
            archive = 0
        for project in projects_list:
            layout_for_project = own_classes.NewFloatLayout()
            # добавляем в активные или не активные проекты
            if project['status'] == 'active':
                active += 1
                title = own_classes.LabelButton(text=project['title'], size_hint=(.7, .25), color=(.72, .39, 0, 1), halign="left", valign="top",
                              pos_hint={"top": .95, "right": .75}, font_size=44)
                title_callback = partial(edit_project, project['project_key'])
                title.bind(size=title.setter('text_size'),  on_release=title_callback)

                description = own_classes.LabelButton(text=project['description'], size_hint=(.7, .7),  halign="left", valign="top", font_size=42,
                                    pos_hint={"top": .7, "right": .75})
                description_callback = partial(edit_project, project['project_key'])
                description.bind(size=description.setter('text_size'), on_release=description_callback)

                move_button = ImageButton(source="icons/projects/move_to_archive.png", size_hint=(.3, .6),
                                          pos_hint={"top": .975, "right": 1})
                but_move_callback = partial(move_to_archive, project['project_key'])
                move_button.bind(on_release=but_move_callback)

                delete_button = ImageButton(source="icons/events/delete.png", size_hint=(.3, .4),
                                            pos_hint={"top": .425, "right": 1})
                but_delete_callback = partial(delete_project, project['project_key'])
                delete_button.bind(on_release=but_delete_callback)

                layout_for_project.add_widget(title)
                layout_for_project.add_widget(description)
                layout_for_project.add_widget(move_button)
                layout_for_project.add_widget(delete_button)
                projects_layout.add_widget(layout_for_project)
            elif project['status'] == 'inactive':
                archive += 1
                title = Label(text=project['title'], size_hint=(.7, .25), color=(.72, .39, 0, 1), halign="left", valign="top",
                              pos_hint={"top": .95, "right": .75}, font_name=constants.main_font, font_size=44)
                title.bind(size=title.setter('text_size'))
                description = Label(text=project['description'], size_hint=(.7, .7),  halign="left", valign="top", font_size=42,
                                    pos_hint={"top": .7, "right": .75}, font_name=constants.main_font)
                description.bind(size=description.setter('text_size'))

                move_button = ImageButton(source="icons/projects/move_from_archive.png", size_hint=(.3, .6),
                                          pos_hint={"top": .975, "right": 1})
                but_move_callback = partial(move_from_archive, project['project_key'])
                move_button.bind(on_release=but_move_callback)

                delete_button = ImageButton(source="icons/events/delete.png", size_hint=(.3, .4),
                                            pos_hint={"top": .425, "right": 1})
                but_delete_callback = partial(delete_project, project['project_key'])
                delete_button.bind(on_release=but_delete_callback)

                layout_for_project.add_widget(title)
                layout_for_project.add_widget(description)
                layout_for_project.add_widget(move_button)
                layout_for_project.add_widget(delete_button)
                archive_projects_layout.add_widget(layout_for_project)
        #
        # Если нет эвентов в списке
        if active == 0:
            l = Label(text='You have not projects', font_size='20sp',  color=(.6, .6, .6, 1), font_name=constants.main_font)
            projects_layout.add_widget(l)
        if archive == 0:
            l = Label(text='Your archive is empty', font_size='20sp',  color=(.6, .6, .6, 1), font_name=constants.main_font)
            archive_projects_layout.add_widget(l)
    else:
        l = Label(text='You have not projects', font_size='20sp',  color=(.6, .6, .6, 1), font_name=constants.main_font)
        projects_layout.add_widget(l)
        l = Label(text='Your archive is empty', font_size='20sp',  color=(.6, .6, .6, 1), font_name=constants.main_font)
        archive_projects_layout.add_widget(l)

# перезаполняет layouts с проектами
def refill_projects_screen(data=None):
    app = App.get_running_app()
    projects_layout = app.root.ids['projects_screen'].ids['projects_layout']
    archive_projects_layout = app.root.ids['archive_projects_screen'].ids['archive_projects_layout']

    def success(request, result):
        for w in projects_layout.walk():
            # Удаляем только FloatLayout
            if w.__class__ == own_classes.NewFloatLayout or w.__class__ == Label:
                projects_layout.remove_widget(w)
        for w in archive_projects_layout.walk():
            if w.__class__ == own_classes.NewFloatLayout or w.__class__ == Label:
                archive_projects_layout.remove_widget(w)
                projects_layout.remove_widget(w)
        fill_projects_screen(data=result)


    def failure(request, error):
        app.error_modal_screen(text_error=constants.connection_error_msg)

    if data == None:
        UrlRequest(
            'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN,
            on_success=success,
            on_failure=failure)
    else:
        success(request=None, result=data)


def fill_one_project_screen(project_request):
    app = App.get_running_app()

    project_data = json.loads(project_request.content.decode())
    if project_data['status'] == 'archive':
        app.previous_screen = 'archive_projects_screen'
    else:
        app.previous_screen = 'projects_screen'
    app.root.ids["one_project_screen"].ids["info_label"].text = ''
    app.root.ids["one_project_screen"].ids["title"].text = project_data['title']
    app.root.ids["one_project_screen"].ids["description"].text = project_data['description']
    app.previous_screen = 'projects_screen'
    app.change_screen('one_project_screen')


def supplement_save():
    app = App.get_running_app()
    addition = app.root.ids["supplement_screen"].ids["addition"].text

    # проверяем заполнение поля
    if addition == '':
        app.root.ids["supplement_screen"].ids["info_label"].text = "You have not completed the addendum"
    else:
        app.root.ids["one_project_screen"].ids["description"].text = \
            f'{app.root.ids["one_project_screen"].ids["description"].text}\n- ' \
            f'{app.root.ids["supplement_screen"].ids["addition"].text}'
        app.change_screen("one_project_screen")
        app.change_screen(app.previous_screen)
        clear_supplement_screen()


def clear_supplement_screen():
    app = App.get_running_app()
    app.root.ids["supplement_screen"].ids["addition"].text = ''
    app.root.ids["supplement_screen"].ids["info_label"].text = ''


def clear_one_project_screen():
    app = App.get_running_app()
    app.root.ids["one_project_screen"].ids["title"].text = ''
    app.root.ids["one_project_screen"].ids["description"].text = ''
    app.root.ids["one_project_screen"].ids["info_label"].text = ''


def edit_project(*args):
    app = App.get_running_app()
    app.previous_screen = 'projects_screen'
    for arg in args:
        if arg.__class__ != own_classes.LabelButton:
            try:
                edit_project_request = requests.get(exist_project_url
                    % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
                Project.operating_project = arg
                fill_one_project_screen(edit_project_request)
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return


def move_to_archive(*args):
    app = App.get_running_app()
    app.previous_screen = 'projects_screen'
    for arg in args:
        if arg.__class__ != ImageButton:
            try:
                edit_project_request = requests.get(exist_project_url
                    % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
                Project.operating_project = arg
                fill_one_project_screen(edit_project_request)
                modal_project_window(name='Remove!', label="Remove project to archive?", command='patch_to')
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return


def move_from_archive(*args):
    app = App.get_running_app()
    app.previous_screen = 'archive_projects_screen'
    for arg in args:
        if arg.__class__ != ImageButton:
            try:
                edit_project_request = requests.get(exist_project_url
                    % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
                Project.operating_project = arg
                fill_one_project_screen(edit_project_request)
                modal_project_window(name='Restore!', label="Restore project from archive?", command='patch_from')
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return


def delete_project(*args):
    app = App.get_running_app()
    app.previous_screen = 'projects_screen'
    for arg in args:
        if arg.__class__ != ImageButton:
            try:
                get_project_request = requests.get(exist_project_url
                    % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
                Project.operating_project = arg
                modal_project_window(name='Delete!', label='Delete this project!?', command='delete')
                fill_one_project_screen(get_project_request)
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return


def modal_project_window(name, label, command):
    app = App.get_running_app()
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
        app.change_screen(app.previous_screen)
        clear_one_project_screen()
        Project.operating_project = ''

    # чтобы перенести в выполненные/удалить
    def yes(*args):
        app = App.get_running_app()
        popup.dismiss()
        if command == 'patch_to':
            try:
                requests.patch(exist_project_url
                    % (constants.LOCAL_ID, Project.operating_project, constants.ID_TOKEN),
                    data=json.dumps({'status': 'inactive'}))
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return
        elif command == 'patch_from':
            try:
                requests.patch(exist_project_url
                    % (constants.LOCAL_ID, Project.operating_project, constants.ID_TOKEN),
                    data=json.dumps({'status': 'active'}))
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return
        elif command == 'delete':
            try:
                requests.delete(exist_project_url
                    % (constants.LOCAL_ID, Project.operating_project, constants.ID_TOKEN))
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return
        refill_projects_screen()
        app.change_screen(app.previous_screen)
        clear_one_project_screen()
        Project.operating_project = ''

    but_no.bind(on_press=no)
    but_yes.bind(on_press=yes)
    popup.open()
