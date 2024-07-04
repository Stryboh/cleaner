import subprocess
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


class FileDeleterApp(BoxLayout):
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        l = ''
        try:
            with open('RM_LIST.txt', 'r') as f:
                l = f.read()

        except Exception as e:
            with open('RM_LIST.txt', 'w') as f:
                f.write('')

        self.status_label = Label(text='Loaded RM_LIST.txt', size_hint_y=None, height='40dp')
        layout.add_widget(self.status_label)

        self.text_input = TextInput(text=l, multiline=False)
        layout.add_widget(self.text_input)

        self.save_button = Button(text='Save to RM_LIST.txt', size_hint_y=None, height='40dp',
                                  on_press=self.on_save_button_click)
        layout.add_widget(self.save_button)

        self.remove_button = Button(text='RM', size_hint_y=None, height='40dp', on_press=self.remove_files)
        layout.add_widget(self.remove_button)

        self.del_tg_button = Button(text='Remove Telegram', size_hint_y=None, height='40dp', on_press=self.del_tg)
        layout.add_widget(self.del_tg_button)

        self.switch_button = Button(text='Switch', size_hint_y=None, height='40dp', on_press=self.switch_to_telegram)
        layout.add_widget(self.switch_button)

        self.add_widget(layout)

    def on_save_button_click(self, instance):
        text = self.text_input.text
        try:
            with open('RM_LIST.txt', 'w') as file:
                file.write(text)
            self.status_label.text = 'List saved successfully.'
        except Exception as e:
            self.status_label.text = f'Error saving list: {e}'

    def remove_files(self, instance):
        removal_list = 'RM_LIST.txt'
        try:
            with open(removal_list, 'r') as file:
                for line in file:
                    subprocess.run(['su', '-c', f'rm -rf {line.strip()}'])
            self.status_label.text = 'Deleted successfully.'
        except Exception as e:
            self.status_label.text = 'RM_LIST.txt does not exist, creating'
            with open('RM_LIST.txt', 'w') as f:
                f.write('')

    def del_tg(self, instance):
        subprocess.run(['su', '-c', 'pm', 'uninstall', '--user', '0', 'org.telegram.messenger'])
        self.status_label.text = 'Telegram removed successfully.'

    def switch_to_telegram(self, instance):
        self.main_app.switch_screen_telegram()
