from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown

from python_code.classes import PWM, Colors, handle_request
from python_code.defaults import manuals, predefineds


class LogicTemplate(GridLayout):
    def __init__(self, zone, **kwargs):
        super(LogicTemplate, self).__init__(**kwargs)

        self.mode = ''
        self.PWMstate = PWM(0, 0, 0, 0, 0, 0)
        self.zone = zone
        self.switched_on = False
        self.index_of_color = None

        self.picker = ColorPicker()
        self.picker_popup = self.color_picker()
        self.Colorstate = Colors()
        self.indicatorlist = []
        self.changelist = []
        self.removelist = []

        self.onToggle = ToggleButton(text='ON', size_hint_y=None, height=40)
        self.onToggle.bind(state=self.toggle_on)

        self.header = GridLayout(cols=2, size_hint_y=None, height=45)
        self.header.add_widget(Label(text=f'Zone {self.zone}:', bold=True, size_hint_y=None, height=40))
        self.header.add_widget(self.onToggle)
        self.add_widget(self.header)

    def toggle_on(self, instance, value):
        if self.switched_on:                            # turn off if it's turned on
            self.switched_on = False
            handle_request(PWM(0, 0, 0, 0, 0, 0), self.zone)
        else:                                           # turn on if it's turned off
            self.switched_on = True
            self.submit_pwm(instance, value)
            sth_else_switched(self.mode, self.zone)     # turn off other modes in this zone
        # print(self.mode, value, self.switched_on, self.onToggle.state)

    def submit_pwm(self, instance, value):
        if self.switched_on:
            self.PWMstate.updateall(self.redSlider.value, self.greenSlider.value, self.blueSlider.value,
                                    self.coolSlider.value, self.warmSlider.value, self.brightSlider.value)
            handle_request(self.PWMstate, self.zone)

    def color_picker(self):
        outside_box = BoxLayout(orientation='vertical')
        inside_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        popup = Popup(title='Pick a color', content=outside_box)

        cancelbutton = Button(text='Cancel', size_hint_y=None, height=40)
        okbutton = Button(text='OK', size_hint_y=None, height=40)
        cancelbutton.bind(on_press=popup.dismiss)
        okbutton.bind(on_press=self.apply_picked_color)

        outside_box.add_widget(self.picker)
        outside_box.add_widget(inside_box)
        inside_box.add_widget(cancelbutton)
        inside_box.add_widget(okbutton)
        return popup

    def apply_picked_color(self, instance):
        print(self.picker.color)
        self.add_color(self.picker.color)
        self.picker_popup.dismiss()

    def get_index(self, instance):
        i = 0
        for button in self.changelist:
            if instance is button:
                return i
            i += 1

        print(self.removelist)
        i = 0
        for button in self.removelist:
            if instance is button:
                return i
            i += 1

        print(i)
        raise AttributeError


class Manual(LogicTemplate):
    def __init__(self, zone, **kwargs):
        super(Manual, self).__init__(zone, **kwargs)
        self.mode = 'manual'
        self.colorcontrols = GridLayout(cols=2)

        self.redSlider = Slider(min=0, max=4095, value=0)
        self.greenSlider = Slider(min=0, max=4095, value=0)
        self.blueSlider = Slider(min=0, max=4095, value=0)
        self.coolSlider = Slider(min=0, max=4095, value=0)
        self.warmSlider = Slider(min=0, max=4095, value=0)
        self.brightSlider = Slider(min=0, max=1000, value=500)

        self.colorcontrols.add_widget(Label(text='Red'))
        self.colorcontrols.add_widget(self.redSlider)
        self.colorcontrols.add_widget(Label(text='Green'))
        self.colorcontrols.add_widget(self.greenSlider)
        self.colorcontrols.add_widget(Label(text='Blue'))
        self.colorcontrols.add_widget(self.blueSlider)
        self.colorcontrols.add_widget(Label(text='Cool'))
        self.colorcontrols.add_widget(self.coolSlider)
        self.colorcontrols.add_widget(Label(text='Warm'))
        self.colorcontrols.add_widget(self.warmSlider)
        self.colorcontrols.add_widget(Label(text='Brightness'))
        self.colorcontrols.add_widget(self.brightSlider)
        self.add_widget(self.colorcontrols)

        self.redSlider.bind(value=self.submit_pwm)
        self.greenSlider.bind(value=self.submit_pwm)
        self.blueSlider.bind(value=self.submit_pwm)
        self.coolSlider.bind(value=self.submit_pwm)
        self.warmSlider.bind(value=self.submit_pwm)
        self.brightSlider.bind(value=self.submit_pwm)


class Predefined(LogicTemplate):
    def __init__(self, zone, **kwargs):
        super(Predefined, self).__init__(zone, **kwargs)
        self.Colorstate.directory = 'predefined'
        self.mode = 'predefined'

        # nested leyouts to display main buttons and an array of selected colors
        self.maincontrols = GridLayout(cols=3, size_hint_y=None, height=40)
        self.colorcontrols = GridLayout(cols=3, padding=(20, 5))

        # creating main buttons
        self.submitButtnon = Button(text='Submit', size_hint_y=None, height=40)
        self.dropdown, self.dropdownButton = self.create_effect_list()
        self.submitButtnon.bind(on_press=self.submit_pwm)
        self.dropdownButton.bind(on_press=self.dropdown.open)
        self.dropdown.bind(on_select=self.select_effect)

        # adding main buttons
        self.maincontrols.add_widget(self.submitButtnon)
        self.maincontrols.add_widget(self.dropdownButton)

        # creating color array buttons
        self.addButton = Button(text='Add', size_hint_y=None, height=40)
        self.addButton.bind(on_press=self.picker_popup.open)

        # adding color array buttons
        self.colorcontrols.add_widget(self.addButton)
        self.add_color(data=[1, 0, 0, 1])
        self.add_color(data=[0, 0, 1, 1])

        self.add_widget(self.maincontrols)
        self.add_widget(self.colorcontrols)

        # TODO add more effects

    def create_effect_list(self):
        dropdown = DropDown()
        self.Colorstate.effect = 'fade'
        dropdown_button = Button(text='Fade')

        fade_button = Button(text='Fade', size_hint_y=None, height=30)
        strobe_button = Button(text='Strobe', size_hint_y=None, height=30)

        fade_button.bind(on_release=lambda btn: dropdown.select(btn.text))
        strobe_button.bind(on_release=lambda btn: dropdown.select(btn.text))
        dropdown.select(fade_button.text)

        dropdown.add_widget(fade_button)
        dropdown.add_widget(strobe_button)

        return dropdown, dropdown_button

    def select_effect(self, instance, value: str):
        self.dropdownButton.text = value
        self.Colorstate.effect = value.lower()

    def add_color(self, data):
        data = list(data)
        data.pop()

        if self.index_of_color is None:
            indicator = Label(color=data)
            indicator.text = str(data)
            changebutton = Button(text='Change color')
            removebutton = Button(text='Remove color')
            changebutton.bind(on_press=self.change_color)
            removebutton.bind(on_press=self.remove_color)
            self.Colorstate.append(data)
            self.indicatorlist.append(indicator)
            self.changelist.append(changebutton)
            self.removelist.append(removebutton)

            self.colorcontrols.add_widget(indicator, 1)
            self.colorcontrols.add_widget(changebutton, 1)
            self.colorcontrols.add_widget(removebutton, 1)
        else:
            self.Colorstate[self.index_of_color] = data
            self.indicatorlist[self.index_of_color].text = str(data)
            self.indicatorlist[self.index_of_color].color = data
            self.index_of_color = None

        if len(self.Colorstate) == 2:
            self.removelist[0].disabled = False

    def change_color(self, instance):
        self.index_of_color = self.get_index(instance)
        print('Changing color with index', self.index_of_color)
        self.picker_popup.open()

    def remove_color(self, instance):
        self.index_of_color = self.get_index(instance)
        print('Removing color with index', self.index_of_color)

        self.colorcontrols.remove_widget(self.indicatorlist[self.index_of_color])
        self.colorcontrols.remove_widget(self.changelist[self.index_of_color])
        self.colorcontrols.remove_widget(self.removelist[self.index_of_color])

        self.Colorstate.pop(self.index_of_color)
        self.indicatorlist.pop(self.index_of_color)
        self.changelist.pop(self.index_of_color)
        self.removelist.pop(self.index_of_color)

        if len(self.Colorstate) == 1:
            self.removelist[0].disabled = True

        self.index_of_color = None

    def submit_pwm(self, instance, value=None):
        # print(self.Colorstate, self)
        if self.switched_on:
            handle_request(self.Colorstate, self.zone)


'''
# LISTA DROPDOWN
class FrameSelect(GridLayout):
    def __init__(self, **kwargs):
        super(FrameSelect, self).__init__(**kwargs)
        self.cols = 2
        self.size_hint_y = None
        self.height = 40

        self.add_widget(Label(text='Wybierz tryb pracy'))
        self.lista = DropDown()

        manual_button = Button(text='Manualny', size_hint_y=None, height=30)
        fade_button = Button(text='Przenikanie', size_hint_y=None, height=30)
        self.lista_button = Button(text='OFF')

        manual_button.bind(on_release=lambda btn: self.lista.select(btn.text))
        fade_button.bind(on_release=lambda btn: self.lista.select(btn.text))

        self.lista.add_widget(manual_button)
        self.lista.add_widget(fade_button)

        self.lista_button.bind(on_release=self.lista.open)
        self.lista.bind(on_select=lambda instance, x: setattr(self.lista_button, 'text', x))
        self.add_widget(self.lista_button)
'''


def sth_else_switched(mode: str, zone: int):
    if mode == 'manual':
        predefineds[zone - 1].onToggle.state = 'normal'
    elif mode == 'predefined':
        manuals[zone - 1].onToggle.state = 'normal'

    # FIXME supposedly works, check with LEDs connected



