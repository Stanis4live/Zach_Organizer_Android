from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


class MyTextInput(TextInput):
    max_value = 12
    background_color = (0, 0, 0, 1)
    foreground_color = (1, 1, 1, 1)
    halign = 'center'

    def input_filter(self, text, from_undo=False):
        if text.isdigit() and len(self.text + text) <= 2:
            new_text = self.text + text
            if int(new_text) <= self.max_value:
                return text
        return ""


class ImageButton(ButtonBehavior, Image):
    pass


class LabelButton(ButtonBehavior, Label):
    font_name = 'fonts/Nunito-Bold.ttf'


KV = ("""
<NewFloatLayout>
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'icons/events/event_back_panel.png'


""")


class NewFloatLayout(FloatLayout):
    def __init__(self, **kwargs):
        super(NewFloatLayout, self).__init__(**kwargs)
