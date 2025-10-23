from kivy.uix.screenmanager import Screen
from kivy.storage.jsonstore import JsonStore
from lib.messages import CreateGameData
import json
import os

CONFIG_FILE = "config.json"

class CreateGameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_back_to_menu')
        self.register_event_type('on_start_new_game')
        

        # Path for local storage (inside the user's home folder)
        self.store_path = os.path.join(os.path.expanduser("~"), ".lichess_game_settings.json")
        self.store = JsonStore(self.store_path)

    def on_back_to_menu(self):
        pass  # To be bound by the workflow manager or App

    def on_start_new_game(self, gameData, lichess_token, serial_port):
        pass  # To be bound by the workflow manager or App


    def on_pre_enter(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                self.lichess_token = data.get("lichess_token", "")
                self.serial_port = data.get("serial_port", "")

        if self.store.exists("settings"):
            data = self.store.get("settings")
            ids = self.ids

            ids.time_control_spinner.text = data.get("time_control", "Real time")
            ids.minutes_slider.value = data.get("minutes", 5)
            ids.increment_slider.value = data.get("increment", 0)
            ids.opponent_spinner.text = data.get("opponent", "Random")
            ids.username_input.text = data.get("username", "")
            ids.stockfish_level_spinner.text = data.get("stockfish_level", "5")

            if data.get("mode", "Casual") == "Rated":
                ids.rated_btn.state = "down"
                ids.casual_btn.state = "normal"
            else:
                ids.casual_btn.state = "down"
                ids.rated_btn.state = "normal"

            # Restore visibility of fields based on opponent
            self.update_opponent_fields(ids.opponent_spinner.text)

    def update_opponent_fields(self, opponent_type):
        username_input = self.ids.username_input
        stockfish_box = self.ids.stockfish_box

        if opponent_type == "User":
            username_input.disabled = False
            username_input.opacity = 1
            stockfish_box.disabled = True
            stockfish_box.opacity = 0
        elif opponent_type == "Stockfish":
            username_input.disabled = True
            username_input.opacity = 0.3
            stockfish_box.disabled = False
            stockfish_box.opacity = 1
        else:  # Random
            username_input.disabled = True
            username_input.opacity = 0.3
            stockfish_box.disabled = True
            stockfish_box.opacity = 0

    def cancel_create_game(self):
        self.dispatch('on_back_to_menu')

    def start_create_game(self, time_control, minutes, increment, mode, opponent, username, stockfish_level):
        print(f"Time control: {time_control}")
        print(f"Minutes: {minutes}")
        print(f"Increment: {increment}")
        print(f"Mode: {mode}")
        print(f"Opponent: {opponent} ({username})")
        print(f"Stockfish level: {stockfish_level}")

        # Save to JSON store
        self.store.put(
            "settings",
            time_control=time_control,
            minutes=minutes,
            increment=increment,
            mode=mode,
            opponent=opponent,
            username=username,
            stockfish_level=stockfish_level
        )

        gameData = CreateGameData( time_control=time_control,
                                   minutes=minutes,
                                   increment=increment,
                                   mode=mode,
                                   opponent=opponent,
                                   username=username,
                                   stockfish_level=stockfish_level )
        

        self.dispatch('on_start_new_game', gameData, self.lichess_token, self.serial_port)
        # Here you’d trigger the actual Lichess API call

