from kivy.uix.screenmanager import SlideTransition
import threading
from kivy.clock import Clock
from lib.game_logic import GameLogic
from lib.messages import GameState, BoardSync, GameInfo

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
        elif state == "wait":
            self.sm.transition = SlideTransition(direction='left')
            self.sm.current = "wait"
        elif state == "config":
            self.sm.transition = SlideTransition(direction='left')
            self.sm.current = "config"
        elif state == "create_game":
            self.sm.transition = SlideTransition(direction='left')
            self.sm.current = "create_game"
        # Add more states/screens as needed

    def bind_menu_events(self, menu_screen):
        menu_screen.bind(on_configure=self.on_configure)
        menu_screen.bind(on_start_game=self.on_start_game)
        menu_screen.bind(on_attach_game=self.on_attach_game)

    def bind_config_events(self, screen):
        screen.bind(on_back_to_menu=self.on_back_to_menu)

    def bind_createGame_events(self, screen):
        screen.bind(on_back_to_menu=self.on_back_to_menu)
        screen.bind(on_start_new_game=self.on_start_new_game)
        
    def on_attach_game(self, instance, lichess_token, serial_port):

        self.go_to("wait")
       
        # Pass the reporting callback to GameLogic
        self.game_logic = GameLogic(
            lichess_token,
            serial_port,
            report_callback=lambda *args, **kwargs: Clock.schedule_once(
                lambda dt: self.reportGameData(*args, **kwargs)
            )
        )

        # Start game loop in a background thread
        threading.Thread(target=self.game_logic.findGame, args=(), daemon=True).start()

    def on_start_new_game(self, instance, gameData, lichess_token, serial_port):

        self.go_to("wait")
       
        # Pass the reporting callback to GameLogic
        self.game_logic = GameLogic(
            lichess_token,
            serial_port,
            report_callback=lambda *args, **kwargs: Clock.schedule_once(
                lambda dt: self.reportGameData(*args, **kwargs)
            )
        )

        # Start game loop in a background thread
        threading.Thread(target=self.game_logic.createNewGame, args=(gameData,), daemon=True).start()

    def on_configure(self, instance):
        self.go_to("config")

    def on_back_to_menu(self, instance):
        print ("holaaa")
        self.go_to("menu")

    def on_start_game(self, instance):
        self.go_to("create_game")


            
    def reportGameData(self, *args, **kwargs):
        obj = args[0] if args else kwargs if kwargs else None

        if isinstance(obj, GameInfo):
            # Set up game screen values before switching
            game_screen = self.sm.get_screen("game") 
            game_screen.setGameInfo(obj)
            self.go_to("game")

            # Start game loop in a background thread
            threading.Thread(target=self.game_logic.play, args=(), daemon=True).start()
        else:
            game_screen = self.sm.get_screen("game")
            game_screen.refresh_state( *args, **kwargs )
