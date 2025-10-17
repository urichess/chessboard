import json
import os
from kivy.uix.screenmanager import Screen, ScreenManager
from ui.ChessGameScreen import ChessGameScreen

CONFIG_FILE = "config.json"

class MenuScreen(Screen):
    def on_pre_enter(self):
        """Load saved values when screen opens."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                self.ids.token_input.text = data.get("lichess_token", "")
                self.ids.serial_input.text = data.get("serial_port", "")

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
        # TODO: Add your game-starting logic here

        # Switch to the ChessGameScreen screen and pass the values
        if not self.manager:
            print("No ScreenManager available to switch screens.")
            return

        if not self.manager.has_screen("chess"):
            self.manager.add_widget(ChessGameScreen(name="chess"))

        chess_screen = self.manager.get_screen("chess")
        chess_screen.lichess_token = lichess_token
        chess_screen.serial_port = serial_port
        self.manager.current = "chess"

