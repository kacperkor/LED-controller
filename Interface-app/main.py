from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.settings import SettingsWithSidebar
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang import Builder

from python_code.uiLogic import Manual, Predefined
from python_code import defaults
from python_code.defaults import zone_number, manuals, predefineds, passwords


Builder.load_file(filename='kv_files/global.kv')
Builder.load_file(filename='kv_files/screens.kv')
Builder.load_file(filename='kv_files/frames.kv')
Builder.load_file(filename='kv_files/logic.kv')

sm = ScreenManager()

# TODO check server status on startup/screen change/in intervals


class ManualFrame(BoxLayout):
    def __init__(self, **kwargs):
        super(ManualFrame, self).__init__(**kwargs)
        for i in range(0, zone_number):
            zone_object = Manual(i + 1)
            manuals.append(zone_object)
            self.add_widget(zone_object)


class PredefinedFrame(BoxLayout):
    def __init__(self, **kwargs):
        super(PredefinedFrame, self).__init__(**kwargs)
        for i in range(0, zone_number):
            zone_object = Predefined(i + 1)
            predefineds.append(zone_object)
            self.add_widget(zone_object)


class PredefinedScreen(Screen):
    def __init__(self, **kwargs):
        super(PredefinedScreen, self).__init__(**kwargs)
        self.toggles = []


class ManualScreen(Screen):
    def __init__(self, **kwargs):
        super(ManualScreen, self).__init__(**kwargs)
        self.toggles = []


class MenuScreen(Screen):
    pass


class ScreenBox(BoxLayout):
    pass


class MainApp(App):
    def build(self):
        self.use_kivy_settings = False
        self.settings_cls = SettingsWithSidebar

        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(ManualScreen(name='manual'))
        sm.add_widget(PredefinedScreen(name='predefined'))
        return sm

    def build_config(self, config):
        # setdefaults(section name in json, dictionary refering to section in configuration file)
        config.setdefaults('general', defaults.general())
        config.setdefaults('zone', defaults.zone())

    def build_settings(self, settings):
        # add_json_panel(Name of the panel on the left and top when active, self.config, path to json file of the panel)
        settings.add_json_panel('General', self.config, data=defaults.general_panel())
        settings.add_json_panel('Zones', self.config, data=defaults.zone_panel())

    def on_config_change(self, config, section, key, value):
        if config is self.config:
            if section == 'general':
                label = Label(text='Changes will be applied after app restart')
                box = BoxLayout(orientation='vertical')
                popup = Popup(title='Infłormation', content=box, size_hint=(None, None), size=(500, 200))
                button = Button(text='OK', on_press=popup.dismiss, size_hint_y=None, height=40)
                box.add_widget(label)
                box.add_widget(button)
                popup.open()
            elif section == 'zone':
                if key[:-1] == 'password_':
                    for i in range(1, zone_number + 1):
                        if int(key[-1]) == i:
                            passwords[i-1] = value
                            # print(self.config.get(section, key))

    def on_start(self):
        # add passwords to passwords[]
        for i in range(1, zone_number + 1):
            passwords.append(self.config.get('zone', f'password_{i}'))


if __name__ == '__main__':
    MainApp().run()
