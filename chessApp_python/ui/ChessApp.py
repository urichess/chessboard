from kivy.app import App
from ui.MenuScreen import MenuScreen
from kivy.uix.screenmanager import Screen, ScreenManager

import argparse
import sys
import requests
#from lib.LichessConnector import LichessConnector
#from lib.BoardSerial import BoardSerial


class ChessApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        return sm


if __name__ == "__main__":
    #parser = argparse.ArgumentParser(description="Run the ChessApp with a Lichess token.")
    #parser.add_argument('--token', required=True, help='Your Lichess API token')
    #parser.add_argument('--serial', required=False, help='Serial to reach serialboard')
    #args = parser.parse_args()

    #serialToUse = args.serial if args.serial else SERIAL_PORT

#    app = ChessApp(args.token, serialToUse)
#    app.run()

    ChessApp().run()

