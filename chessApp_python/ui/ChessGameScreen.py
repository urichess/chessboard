from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty

class ChessGameScreen(Screen):
    """A simple screen shown when a game starts.

    Stores the lichess token and serial port (set by MenuScreen) so game
    initialization code can access them.
    """

    lichess_token = StringProperty("")
    serial_port = StringProperty("")

    player_name = StringProperty("Player")
    opponent_name = StringProperty("Opponent")
    player_time = StringProperty("05:00")
    opponent_time = StringProperty("05:00")
    player_increment = NumericProperty(3)
    opponent_increment = NumericProperty(3)
    player_last_move = StringProperty("-")
    opponent_last_move = StringProperty("-")

    active_player = StringProperty("player")  # 'player' or 'opponent'

    def on_pre_enter(self):
        """Called before the screen is shown. Prints received values for now."""
        print(f"ChessGameScreen: starting with token={self.lichess_token!r}, serial={self.serial_port!r}")
        # TODO: initialize game, connectors, board serial, etc.

    def on_leave(self):
        """Optional cleanup when leaving the game screen."""
        print("Leaving ChessGameScreen")
