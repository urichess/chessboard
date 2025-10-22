import json
import os
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.app import App
from kivy.properties import StringProperty

CONFIG_FILE = "config.json"

class ConfigScreen(Screen):    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_back_to_menu')

    def on_back_to_menu(self):
        pass  # To be bound by the workflow manager or App

    def on_pre_enter(self):
        """Load saved values when screen opens."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                self.ids.token_input.text = data.get("lichess_token", "")
                self.ids.serial_input.text = data.get("serial_port", "")

        

    def on_save(self):
        """Save configuration to file."""
        lichess_token = self.ids.token_input.text.strip()
        serial_port = self.ids.serial_input.text.strip()

        data = {
            "lichess_token": lichess_token,
            "serial_port": serial_port
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)

        print("Configuration saved.")

        self.dispatch('on_back_to_menu')

    def on_cancel(self):
        """Return to the previous screen without saving."""
        self.dispatch('on_back_to_menu')