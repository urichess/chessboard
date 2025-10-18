from kivy.uix.screenmanager import SlideTransition
import threading
from lib.LichessConnector import LichessConnector
from lib.BoardSerial import BoardSerial

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
        game_screen.lichess_token = lichess_token
        game_screen.serial_port = serial_port



        
        self.go_to("game")

        # Start game loop in a background thread
        threading.Thread(target=self.run_game_loop, args=(lichess_token, serial_port,), daemon=True).start()

    def run_game_loop(self, lichess_token, serial_port):

        board = BoardSerial(serial_port, SERIAL_BAUDRATE) 

        lichess = LichessConnector(lichess_token)
        #self.username = lichess.getUsername()
        
        game = lichess.findGame()

        if not game:
            print("No game found.")
            return

        currentBoard = game.waitMyTurn()
        while currentBoard is not None:
            if currentBoard.move_stack:
                previousBoard = currentBoard.copy(stack=True)
                last_move = previousBoard.pop()
                san = previousBoard.san(last_move)
                print(f"Opponent's move: \033[31m{san}\033[0m")
            else:
                print("You start.")

            board.sync(currentBoard)
            aMove = board.getMove(currentBoard)

            # confirmation??
            game.sendMove(aMove)
            currentBoard = game.waitMyTurn()
