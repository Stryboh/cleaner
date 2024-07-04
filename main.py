from kivy.app import async_runTouchApp
from kivy.uix.screenmanager import ScreenManager, Screen
from telegram import TelegramApp
import filedeleter
import asyncio

class MainApp:
    def build(self):
        self.screen_manager = ScreenManager()

        filedeleter_screen = Screen(name='filedeleter_app')
        filedeleter_app = filedeleter.FileDeleterApp(main_app=self)
        filedeleter_screen.add_widget(filedeleter_app)
        self.screen_manager.add_widget(filedeleter_screen)

        telegram_screen = Screen(name='telegram_app')
        telegram_app = TelegramApp(main_app=self)
        telegram_screen.add_widget(telegram_app)
        self.screen_manager.add_widget(telegram_screen)

        return self.screen_manager

    def switch_screen_deleter(self):
        self.screen_manager.current = 'filedeleter_app'

    def switch_screen_telegram(self):
        self.screen_manager.current = 'telegram_app'

    async def async_run(self):
        await async_runTouchApp(self.build(), async_lib='asyncio')

if __name__ == '__main__':
    app = MainApp()
    asyncio.run(app.async_run())
