from kivy.uix.screenmanager import Screen
from kivy.storage.jsonstore import JsonStore
import os

class CreateGameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_back_to_menu')

        # Path for local storage (inside the user's home folder)
        self.store_path = os.path.join(os.path.expanduser("~"), ".lichess_game_settings.json")
        self.store = JsonStore(self.store_path)

    def on_back_to_menu(self):
        pass  # To be bound by the workflow manager or App
      

    def on_pre_enter(self):
        """
        When the screen is about to be displayed, load saved settings.
        """
        if self.store.exists("settings"):
            data = self.store.get("settings")
            ids = self.ids

            ids.hours_spinner.text = data.get("hours", "0 h")
            ids.minutes_spinner.text = data.get("minutes", "5 m")
            ids.seconds_spinner.text = data.get("seconds", "0 s")
            ids.increment_spinner.text = data.get("increment", "0 s")
            ids.opponent_spinner.text = data.get("opponent", "Random")
            ids.username_input.text = data.get("username", "")
            ids.color_spinner.text = data.get("color", "Random")
            ids.stockfish_level_spinner.text = data.get("stockfish_level", "5")

            # Update visibility based on opponent type
            self.update_opponent_fields(ids.opponent_spinner.text)

    def update_opponent_fields(self, opponent_type):
        """
        Show or hide fields depending on the selected opponent type.
        """
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
        print ("kkkk")
        self.dispatch('on_back_to_menu')

    def start_create_game(self, hours, minutes, seconds, increment, opponent, username, color, stockfish_level):
        """
        Start the game and save current settings to memory.
        """
        print(f"Time: {hours} {minutes} {seconds}")
        print(f"Increment: {increment}")
        print(f"Opponent: {opponent} ({username})")
        print(f"Stockfish level: {stockfish_level}")
        print(f"Color: {color}")

        # Save current settings to JSON
        self.store.put(
            "settings",
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            increment=increment,
            opponent=opponent,
            username=username,
            color=color,
            stockfish_level=stockfish_level,
        )

        # Here you would add the logic to create the game on Lichess via API
