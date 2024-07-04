from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from telethon import TelegramClient
import credentials
import asyncio
from kivy.clock import Clock

class CustomPopup(Popup):
    def __init__(self, **kwargs):
        self.is_password = kwargs.pop('is_password', False)
        self.on_confirm = kwargs.pop('on_confirm', None)
        super().__init__(**kwargs)

        self.size_hint = (0.9, 0.5)
        self.auto_dismiss = False

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.input_field = TextInput(password=self.is_password, multiline=False)
        layout.add_widget(self.input_field)

        confirm_button = Button(text='Confirm', size_hint_y=None, height='40dp', on_press=self.confirm)
        layout.add_widget(confirm_button)

        self.add_widget(layout)

    def confirm(self, instance):
        if self.on_confirm:
            self.on_confirm(self.input_field.text)
        self.dismiss()

class TelegramApp(BoxLayout):
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app
        self.load_credentials()
        self.client = TelegramClient('telegram_session', self.api_id, self.api_hash)

        self.orientation = 'vertical'
        self.status_label = Label(text='Initializing...', size_hint_y=None, height='40dp')
        self.add_widget(self.status_label)

        Clock.schedule_once(lambda dt: self.init_client())

    def init_client(self):
        asyncio.ensure_future(self.async_init_client())

    async def async_init_client(self):
        try:
            await self.client.connect()
            print('Connected')
            if await self.client.is_user_authorized():
                self.switch_to_logged_in_ui()
            else:
                self.switch_to_login_ui()
        except Exception as e:
            self.status_label.text = f'Error: {e}'
            print(f'Error during connection: {e}')

    def load_credentials(self):
        try:
            self.api_id = credentials.api_id()
            self.api_hash = credentials.api_hash()
            self.phone = credentials.phone()
        except Exception as e:
            self.api_id = None
            self.api_hash = None
            self.phone = None
            print(f'Error loading credentials: {e}')

    def switch_to_login_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.status_label = Label(text='Enter your Telegram phone number', size_hint_y=None, height='40dp')
        layout.add_widget(self.status_label)

        self.phone_input = TextInput(hint_text='Enter your phone number', multiline=False, size_hint_y=None, height='40dp')
        layout.add_widget(self.phone_input)

        self.login_button = Button(text='Login', size_hint_y=None, height='40dp', on_press=self.login)
        layout.add_widget(self.login_button)

        self.add_widget(layout)

    def switch_to_logged_in_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        l = ''
        try:
            with open('DIALOGS_LIST.txt', 'r') as f:
                l = f.read()
        except Exception as e:
            print(f'Error reading DIALOGS_LIST.txt: {e}')
            with open('DIALOGS_LIST.txt', 'w') as f:
                f.write('')

        self.status_label = Label(text='Logged in successfully!', size_hint_y=None, height='40dp')
        layout.add_widget(self.status_label)

        self.dialog_input = TextInput(text=l, multiline=False)
        layout.add_widget(self.dialog_input)

        self.save_button = Button(text='Save to DIALOGS_LIST.txt', size_hint_y=None, height='40dp', on_press=self.save_DIALOGS_LIST)
        layout.add_widget(self.save_button)

        self.delete_button = Button(text='Delete Dialogs', size_hint_y=None, height='40dp', on_press=self.delete_dialogs)
        layout.add_widget(self.delete_button)

        self.switch_button = Button(text='Switch', size_hint_y=None, height='40dp', on_press=self.switch_to_file_deleter)
        layout.add_widget(self.switch_button)

        self.add_widget(layout)

    def login(self, instance):
        phone = self.phone_input.text.strip()

        if not self.api_id or not self.api_hash or not phone:
            self.status_label.text = 'Invalid credentials!'
            return

        Clock.schedule_once(lambda dt: asyncio.ensure_future(self.perform_login(phone)))

    async def perform_login(self, phone):
        try:
            if not await self.client.is_user_authorized():
                await self.client.send_code_request(phone)
                self.show_code_input_popup()
            else:
                self.status_label.text = 'Logged in successfully!'
                self.switch_to_logged_in_ui()
        except Exception as e:
            self.status_label.text = f'Error during login: {e}'
            print(f'Error during login: {e}')

    def show_code_input_popup(self):
        self.popup = CustomPopup(
            title='Enter the code sent to your phone',
            is_password=False,
            on_confirm=self.confirm_code
        )
        self.popup.open()

    def confirm_code(self, code):
        Clock.schedule_once(lambda dt: asyncio.ensure_future(self.perform_confirm_code(code)))

    async def perform_confirm_code(self, code):
        try:
            await self.client.sign_in(self.phone, code)
            self.popup.dismiss()
        except Exception as e:
            self.popup.dismiss()
            self.show_password_input_popup()
            print(f'Error during code confirmation: {e}')
            return

        self.status_label.text = 'Logged in successfully!'
        self.switch_to_logged_in_ui()

    def show_password_input_popup(self):
        self.popup = CustomPopup(
            title='Enter your two-factor authentication password',
            is_password=True,
            on_confirm=self.confirm_password
        )
        self.popup.open()

    def confirm_password(self, password):
        Clock.schedule_once(lambda dt: asyncio.ensure_future(self.perform_confirm_password(password)))

    async def perform_confirm_password(self, password):
        try:
            await self.client.sign_in(password=password)
            self.popup.dismiss()
        except Exception as e:
            self.status_label.text = f'Error: {e}'
            print(f'Error during password confirmation: {e}')
            return

        self.status_label.text = 'Logged in successfully!'
        self.switch_to_logged_in_ui()

    def save_DIALOGS_LIST(self, instance):
        DIALOGS_LIST = self.dialog_input.text.split(',')
        try:
            with open('DIALOGS_LIST.txt', 'w') as f:
                for item in DIALOGS_LIST:
                    f.write(f"{item.strip()}\n")
            self.status_label.text = 'DIALOGS_LIST.txt updated!'
        except Exception as e:
            self.status_label.text = f'Error saving DIALOGS_LIST: {e}'
            print(f'Error saving DIALOGS_LIST: {e}')

    def delete_dialogs(self, instance):
        Clock.schedule_once(lambda dt: asyncio.ensure_future(self.perform_delete_dialogs()))

    async def perform_delete_dialogs(self):
        try:
            with open('DIALOGS_LIST.txt', 'r') as f:
                DIALOGS_LIST = [line.strip() for line in f]

            dialog_list = await self.client.get_dialogs()
            for dialog in dialog_list:
                if dialog.title in DIALOGS_LIST:
                    await self.client.delete_dialog(dialog)
                    self.status_label.text = f'{dialog.title} ==> Deleted'
        except Exception as e:
            self.status_label.text = f'Error deleting dialogs: {e}'
            print(f'Error deleting dialogs: {e}')

    def switch_to_file_deleter(self, instance):
        self.main_app.switch_screen_deleter()
