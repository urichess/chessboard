import json
import os
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.app import App
from ui.ChessGameScreen import ChessGameScreen

CONFIG_FILE = "config.json"

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_start_game')
        self.register_event_type('on_attach_game')
        self.register_event_type('on_configure')

    def on_start_game(self, lichess_token, serial_port):
        pass  # To be bound by the workflow manager or App

    def on_attach_game(self, lichess_token, serial_port):
        pass  # To be bound by the workflow manager or App

    def on_configure(self):
        pass  # To be bound by the workflow manager or App

    def on_pre_enter(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                self.lichess_token = data.get("lichess_token", "")
                self.serial_port = data.get("serial_port", "")

    def configure(self):
        self.dispatch('on_configure')


    def attach_game(self):
        """Called when 'Start Game' is pressed."""
        lichess_token = self.lichess_token 
        serial_port = self.serial_port

        if not lichess_token or not serial_port:
            print("Please, configure both lichess token and serial port.")
            return

        # Save to file
        data = {
            "lichess_token": lichess_token,
            "serial_port": serial_port
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)

        print(f"Starting game with token: {lichess_token} and serial port: {serial_port}")
        # Dispatch event instead of direct workflow call
        self.dispatch('on_attach_game', lichess_token, serial_port)

    def start_game(self):
        """Called when 'Start Game' is pressed."""
        lichess_token = self.ids.token_input.text.strip()
        serial_port = self.ids.serial_input.text.strip()

        if not lichess_token or not serial_port:
            print("Please fill in both fields.")
            return

        # Save to file
        data = {
            "lichess_token": lichess_token,
            "serial_port": serial_port
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)

        print(f"Starting game with token: {lichess_token} and serial port: {serial_port}")
        # Dispatch event instead of direct workflow call
        self.dispatch('on_start_game', lichess_token, serial_port)

