import json
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.network.urlrequest import UrlRequest
import own_classes
from own_classes import ImageButton
from functools import partial
import constants


class Purchase:
    operating_purchase = ''


exist_purchase_url = 'https://zach-mobile-default-rtdb.firebaseio.com/%s/shop_list/%s.json?auth=%s'


def save_new_purchase(text):
    app = App.get_running_app()
    if text:
        purchase_data_for_load = {'purchase_text': text, 'status': 'active'}
        if Purchase.operating_purchase == '':
            # requests.post присваивает запросу ключ
            requests.post(
                'https://zach-mobile-default-rtdb.firebaseio.com/%s/shop_list.json?auth=%s'
                % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps(purchase_data_for_load))
        # если purchase уже существует, то меняем
        else:
            requests.patch(exist_purchase_url
                % (constants.LOCAL_ID, Purchase.operating_purchase, constants.ID_TOKEN),
                data=json.dumps(purchase_data_for_load))
            Purchase.operating_purchase = ''
        refill_shopping_list_layout()
        app.change_screen("shopping_list_screen")


def shopping_list_fill(data):
    app = App.get_running_app()

    shopping_list_layout = app.root.ids['shopping_list_screen'].ids['shopping_layout']
    # Проверка на наличие заданий
    if 'shop_list' in data:
        # словарь словарей
        purchases = data['shop_list']
        # ключи событий
        purchase_keys = purchases.keys()
        # Сортировка заданий
        purchase_list = []
        # добавляем в словарь второго порядка по ключам поля с ключами 'purchase_key' и значениями - ключ
        for purchase_key in purchase_keys:
            purchases[purchase_key]['purchase_key'] = str(purchase_key)
            purchase_list.append(purchases[purchase_key])

        purchase_list = sorted(purchase_list, key=lambda x: (x['status'], ''),
                            reverse=False)
        # Заполнение
        for purchase in purchase_list:
            layout_for_purchase = own_classes.NewFloatLayout()
            # добавляем в активные или не активные события
            if purchase['status'] == 'active':
                description = own_classes.LabelButton(text=purchase['purchase_text'],  size_hint=(.7, .8),
                                pos_hint={"top": .87, "right": .75}, halign="left", valign="top", font_size=32)
                description_callback = partial(edit_purchase, purchase["purchase_key"])
                description.bind(size=description.setter('text_size'), on_release=description_callback)

                checkbox = CheckBox(size_hint=(.25, .25), active=False,
                                          pos_hint={"top": .95, "right": 1})
                checkbox_callback = partial(checkbox_active, arg=purchase['purchase_key'])
                checkbox.bind(active=checkbox_callback)

                copy_button = ImageButton(source="icons/events/copy.png", size_hint=(.25, .3),
                                          pos_hint={"top": .65, "right": 1})
                but_copy_callback = partial(copy_purchase, purchase["purchase_key"])
                copy_button.bind(on_release=but_copy_callback)

                delete_button = ImageButton(source="icons/events/delete.png", size_hint=(.25, .3),
                                            pos_hint={"top": .35, "right": 1})
                but_delete_callback = partial(delete_purchase, purchase["purchase_key"])
                delete_button.bind(on_release=but_delete_callback)

                layout_for_purchase.add_widget(description)
                layout_for_purchase.add_widget(copy_button)
                layout_for_purchase.add_widget(checkbox)
                layout_for_purchase.add_widget(delete_button)
                shopping_list_layout.add_widget(layout_for_purchase)
            elif purchase['status'] == 'inactive':
                description = Label(markup=True, text=f"[s]{purchase['purchase_text']}[/s]", size_hint=(.7, .8),
                                pos_hint={"top": .87, "right": .75}, halign="left", valign="top", font_size=42)
                description_callback = partial(edit_purchase, purchase["purchase_key"])
                description.bind(size=description.setter('text_size'), on_release=description_callback)

                checkbox = CheckBox(size_hint=(.25, .25), active=True,
                                          pos_hint={"top": .95, "right": 1})
                checkbox_callback = partial(checkbox_active, arg=purchase['purchase_key'])
                checkbox.bind(active=checkbox_callback)

                copy_button = ImageButton(source="icons/events/copy.png", size_hint=(.25, .3),
                                          pos_hint={"top": .65, "right": 1})
                but_copy_callback = partial(copy_purchase, purchase["purchase_key"])
                copy_button.bind(on_release=but_copy_callback)

                delete_button = ImageButton(source="icons/events/delete.png", size_hint=(.25, .3),
                                            pos_hint={"top": .35, "right": 1})
                but_delete_callback = partial(delete_purchase, purchase["purchase_key"])
                delete_button.bind(on_release=but_delete_callback)

                layout_for_purchase.add_widget(description)
                layout_for_purchase.add_widget(checkbox)
                layout_for_purchase.add_widget(copy_button)
                layout_for_purchase.add_widget(delete_button)
                shopping_list_layout.add_widget(layout_for_purchase)

    # Нет никаких заданий в списке
    else:
        l = Label(text='Your shopping list is empty', font_size='20sp',  color=(.6, .6, .6, 1), font_name=constants.main_font)
        shopping_list_layout.add_widget(l)


def edit_purchase(*args):
    app = App.get_running_app()
    for arg in args:
        if arg.__class__ != own_classes.LabelButton:
            # по ключу мы достаём запись
            try:
                edit_purchase_request = requests.get(exist_purchase_url
                    % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
                Purchase.operating_purchase = arg
                modal_edit_purchase_window(command='edit', purchase_request=edit_purchase_request, text='Edit purchase')
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)


def copy_purchase(*args):
    app = App.get_running_app()
    for arg in args:
        if arg.__class__ != ImageButton:
            try:
                copy_purchase_request = requests.get(exist_purchase_url
                    % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
                modal_edit_purchase_window(command='copy', purchase_request=copy_purchase_request, text='Copy purchase')
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)


def checkbox_active(checkbox, value, arg):
    if value:
        try:
            requests.patch(exist_purchase_url
                % (constants.LOCAL_ID, arg, constants.ID_TOKEN),
                data=json.dumps({'status': 'inactive'}))
        except Exception:
            app = App.get_running_app()
            app.error_modal_screen(text_error=constants.connection_error_msg)
            return
    else:
        try:
            requests.patch(exist_purchase_url
                % (constants.LOCAL_ID, arg, constants.ID_TOKEN),
                data=json.dumps({'status': 'active'}))
        except Exception:
            app = App.get_running_app()
            app.error_modal_screen(text_error=constants.connection_error_msg)
            return
    refill_shopping_list_layout()


def delete_purchase(*args):
    app = App.get_running_app()
    for arg in args:
        if arg.__class__ != ImageButton:
            try:
                delete_purchase_request = requests.get(exist_purchase_url
                    % (constants.LOCAL_ID, arg, constants.ID_TOKEN))
                Purchase.operating_purchase = arg
                modal_edit_purchase_window(command='delete', purchase_request=delete_purchase_request, text='Delete this purchase?')
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)


def refill_shopping_list_layout(data=None):
    app = App.get_running_app()
    shopping_list_layout = app.root.ids['shopping_list_screen'].ids['shopping_layout']

    def success(request, result):
        for w in shopping_list_layout.walk():
            # Удаляем только FloatLayout
            if w.__class__ == own_classes.NewFloatLayout or w.__class__ == Label or w.__class__ == CheckBox:
                shopping_list_layout.remove_widget(w)
        shopping_list_fill(data=result)


    def failure(request, error):
        app.error_modal_screen(text_error=constants.connection_error_msg)

    if data == None:
        UrlRequest(
            'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN,
            on_success=success,
            on_failure=failure)
    else:
        success(request=None, result=data)


def modal_edit_purchase_window(command, purchase_request, text):
    app = App.get_running_app()
    purchase_data = json.loads(purchase_request.content.decode())

    # Создаём модальное окно
    bl = BoxLayout(orientation='vertical')
    t_i = TextInput(text=purchase_data['purchase_text'], size_hint=  (1, .7),
            pos_hint={'top': .75, 'right': 1}, background_color=(0,0,0,1), foreground_color=(1, 1, 1, 1), font_size=40)
    bl.add_widget(t_i)
    bl2 = BoxLayout(orientation='horizontal', size_hint=  (1, .3),
            pos_hint={'top': .3, 'right': 1})
    but_no = Button(text="Don't save", font_size=40, size_hint=(.3, .7))
    but_yes = Button(text=text, font_size=40, size_hint=(.3, .7))
    bl2.add_widget(but_no)
    bl2.add_widget(but_yes)
    bl.add_widget(bl2)
    popup = Popup(title_align= 'center', title=text, content=bl, size_hint=(1, .45), pos_hint={"x": 0, "top": .78},
                  auto_dismiss=False)

    # если не сохранять
    def no(*args):
        popup.dismiss()
        app.change_screen("shopping_list_screen")

    # чтобы изменить пункт
    def yes(*args):
        popup.dismiss()
        if command == 'edit':
            try:
                requests.patch(exist_purchase_url
                    % (constants.LOCAL_ID, Purchase.operating_purchase, constants.ID_TOKEN),
                    data=json.dumps({'purchase_text': t_i.text}))
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return
        elif command == 'copy':
            try:
                requests.post(
                    'https://zach-mobile-default-rtdb.firebaseio.com/%s/shop_list.json?auth=%s'
                    % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps({'purchase_text': t_i.text, 'status': 'active'}))
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return

        elif command == 'delete':
            try:
                requests.delete(exist_purchase_url
                    % (constants.LOCAL_ID, Purchase.operating_purchase, constants.ID_TOKEN))
            except Exception:
                app.error_modal_screen(text_error=constants.connection_error_msg)
                return

        refill_shopping_list_layout()
        Purchase.operating_purchase = ''

    but_no.bind(on_press=no)
    but_yes.bind(on_press=yes)
    popup.open()


def modal_delete_window(command, *args):
    if command == 'delete':
        text_label = 'Delete this shopping list?'
        text_popup = 'Delete this shopping list'
    elif command == "delete_with_added":
        text_label = 'Create new shopping list?'
        text_popup = 'Create new shopping list'
    else:
        text_label = ''
        text_popup = ''
    # Создаём модальное окно
    bl = BoxLayout(orientation='vertical')
    l = Label(text=text_label, font_size=40, font_name=constants.main_font)
    bl.add_widget(l)
    bl2 = BoxLayout(orientation='horizontal')
    but_no = Button(text='No', font_size=40, size_hint=(.3, .4))
    but_yes = Button(text='Yes', font_size=40, size_hint=(.3, .4))
    bl2.add_widget(but_no)
    bl2.add_widget(but_yes)
    bl.add_widget(bl2)
    popup = Popup(title_align= 'center', title=text_popup, content=bl, size_hint=(1, .45), pos_hint={"x": 0, "top": .78},
                  auto_dismiss=False)

    def no(*args):
        popup.dismiss()

    # чтобы перенести в выполненные/удалить
    def yes(*args):
        app = App.get_running_app()
        popup.dismiss()
        try:
            result = requests.get(
                'https://zach-mobile-default-rtdb.firebaseio.com/' + constants.LOCAL_ID + '.json?auth=' + constants.ID_TOKEN)
            data = json.loads(result.content.decode())
            if 'shop_list' in data:
                # словарь словарей
                purchases = data['shop_list']
                # ключи словаря - идентификаторы в базе
                purchase_keys = purchases.keys()
                # проходим по значениям через ключи словаря
                if command == 'delete':
                    for purchase_key in purchase_keys:
                        try:
                            requests.delete(exist_purchase_url
                                % (constants.LOCAL_ID, purchase_key, constants.ID_TOKEN))
                        except Exception:
                            app.error_modal_screen(text_error=constants.connection_error_msg)
                            return
                    Purchase.operating_purchase = ''
                    refill_shopping_list_layout()
                elif command == 'delete_with_added':
                    # Второе модальное окно, предлагающее сохранить активные покупки
                    bl = BoxLayout(orientation='vertical')
                    l = Label(text='Do you want to save pending purchases?', size_hint=(1, .8),
                                    pos_hint={'top': .1, 'right': 1}, font_name=constants.main_font)
                    bl.add_widget(l)
                    bl2 = BoxLayout(orientation='horizontal')
                    but_cancel = Button(text='Cancel', font_size=40, size_hint=(.3, .35))
                    but_no = Button(text="Don't", font_size=40, size_hint=(.3, .35))
                    but_yes = Button(text='Save', font_size=40, size_hint=(.3, .35))
                    bl2.add_widget(but_cancel)
                    bl2.add_widget(but_no)
                    bl2.add_widget(but_yes)
                    bl.add_widget(bl2)
                    small_popup = Popup(title_align= 'center', title='Save purchases?', content=bl, size_hint=(1, .45), pos_hint={"x": 0, "top": .78},
                                  auto_dismiss=False)

                    def small_no(*args):
                        small_popup.dismiss()
                        for purchase_key in purchase_keys:
                            try:
                                requests.delete(exist_purchase_url
                                    % (constants.LOCAL_ID, purchase_key, constants.ID_TOKEN))
                            except Exception:
                                app.error_modal_screen(text_error=constants.connection_error_msg)
                                return
                        Purchase.operating_purchase = ''
                        refill_shopping_list_layout()

                    def small_cancel(*args):
                        small_popup.dismiss()

                    # если хотим оставить незавершенные покупки
                    def small_yes(*args):
                        small_popup.dismiss()
                        inactive_purchases = set()
                        for purchase_key in purchase_keys:
                            if purchases[purchase_key]['status'] == 'inactive':
                                inactive_purchases.add(purchase_key)
                        if inactive_purchases:
                            for purchase in inactive_purchases:
                                try:
                                    requests.delete(exist_purchase_url
                                        % (constants.LOCAL_ID, purchase, constants.ID_TOKEN))
                                except Exception:
                                    app.error_modal_screen(text_error=constants.connection_error_msg)
                                    return
                            Purchase.operating_purchase = ''
                            refill_shopping_list_layout()

                    but_cancel.bind(on_press=small_cancel)
                    but_no.bind(on_press=small_no)
                    but_yes.bind(on_press=small_yes)
                    small_popup.open()
        except Exception:
            app.error_modal_screen(text_error=constants.connection_error_msg)
            return

    but_no.bind(on_press=no)
    but_yes.bind(on_press=yes)
    popup.open()
