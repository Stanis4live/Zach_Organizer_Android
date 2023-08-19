from kivy.app import App


am_inactive = "icons/time/am_black.png"
am_active = "icons/time/am_blue.png"
pm_inactive = "icons/time/pm_black.png"
pm_active = "icons/time/pm_blue.png"


def time_up(text, max_value, id):
    if text == '':
        new_value = '00'
    elif text == max_value:
        new_value = '00'
    else:
        new_value = str(int(text) + 1)

    if len(new_value) == 1:
        new_value = '0' + new_value

    app = App.get_running_app()
    app.root.ids['time_screen'].ids[id].text = new_value


def time_down(text, max_value, id):
    if text == '':
        new_value = '00'
    elif text == '00':
        new_value = max_value
    else:
        new_value = str(int(text) - 1)

    if len(new_value) == 1:
        new_value = '0' + new_value

    app = App.get_running_app()
    app.root.ids['time_screen'].ids[id].text = new_value


# Заполняет new_event_screen из time_screen
def add_time():
    app = App.get_running_app()
    hours = app.root.ids['time_screen'].ids['hour'].text
    minutes = app.root.ids['time_screen'].ids['minute'].text
    if hours == '' or int(hours) > 12:
        app.root.ids["time_screen"].ids["info_label"].text = 'Please fill in the hours field correctly'
        return

    if minutes == '' or int(hours) > 59:
        app.root.ids["time_screen"].ids["info_label"].text = 'Please fill in the minutes field correctly'
        return

    if len(hours) == 1:
        hours = f'0{hours}'
    if len(minutes) == 1:
        minutes = f'0{minutes}'

    if app.root.ids['time_screen'].ids['am'].source == am_active and hours == '12':
        time = f'00:{minutes}:00'
    elif app.root.ids['time_screen'].ids['pm'].source == pm_active and hours != '12':
        time = f'{int(hours) + 12}:{minutes}:00'
    else:
        time = f'{hours}:{minutes}:00'
    app.root.ids["new_event_screen"].ids["chosen_time"].text = time
    app.change_screen("new_event_screen")


# Заполняем time_screen из new_event_screen
def time_fill():
    app = App.get_running_app()
    current_time = app.root.ids["new_event_screen"].ids["chosen_time"].text
    if current_time != 'time':
        if 22 > int(current_time[:2]) > 12:
            app.root.ids['time_screen'].ids['hour'].text = f'0{int(current_time[:2]) - 12}'
        elif int(current_time[:2]) > 21:
            app.root.ids['time_screen'].ids['hour'].text = f'{int(current_time[:2]) - 12}'
        else:
            app.root.ids['time_screen'].ids['hour'].text = current_time[:2]
        app.root.ids['time_screen'].ids['minute'].text = current_time[3:5]


def switch_am_pm(but_name):
    app = App.get_running_app()
    if but_name == 'am':
        if app.root.ids['time_screen'].ids['am'].source == am_inactive:
            app.root.ids['time_screen'].ids['am'].source  = am_active
            app.root.ids['time_screen'].ids['pm'].source = pm_inactive
    elif but_name == 'pm':
        if app.root.ids['time_screen'].ids['pm'].source == pm_inactive:
            app.root.ids['time_screen'].ids['am'].source = am_inactive
            app.root.ids['time_screen'].ids['pm'].source = pm_active









