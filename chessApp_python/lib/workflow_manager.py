from kivy.uix.screenmanager import SlideTransition
import threading
from kivy.clock import Clock
from lib.game_logic import GameLogic

SERIAL_BAUDRATE = 115200

class WorkflowManager:
    def __init__(self, screen_manager):
        self.sm = screen_manager
        self.state = "menu"

    def go_to(self, state):
        self.state = state
        if state == "menu":
            self.sm.transition = SlideTransition(direction='right')
            self.sm.current = "menu"
        elif state == "game":
            self.sm.transition = SlideTransition(direction='left')
            self.sm.current = "game"
        # Add more states/screens as needed

    def bind_menu_events(self, menu_screen):
        menu_screen.bind(on_start_game=self.on_start_game)

    def on_start_game(self, instance, lichess_token, serial_port):
        # Set up game screen values before switching
        game_screen = self.sm.get_screen("game") 
        self.go_to("game")

        # Start game loop in a background thread
        threading.Thread(target=self.run_game_loop, args=(lichess_token, serial_port,), daemon=True).start()

    def run_game_loop(self, lichess_token, serial_port):
        game_logic = GameLogic(lichess_token, serial_port)
        game_logic.play()

        