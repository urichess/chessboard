from kivy.uix.screenmanager import SlideTransition
import threading
from kivy.clock import Clock
from lib.game_logic import GameLogic
from lib.messages import GameState

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

        # Pass the reporting callback to GameLogic
        #self.game_logic = GameLogic(
        #    lichess_token,
        #    serial_port,
        #    report_callback=lambda **kwargs: Clock.schedule_once(lambda dt: self.reportGameData(**kwargs))
        #)

        self.game_logic = GameLogic(
            lichess_token,
            serial_port,
            report_callback=lambda *args, **kwargs: Clock.schedule_once(
                lambda dt: self.reportGameData(*args, **kwargs)
            )
        )

        # Start game loop in a background thread
        threading.Thread(target=self.game_logic.play, args=(), daemon=True).start()

    def reportGameData(self, message: GameState):
        game_screen = self.sm.get_screen("game")
        game_screen.refresh_state( message )
