from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.clock import Clock
from lib.messages import GameState, BoardSync

class ChessGameScreen(Screen):
    """A simple screen shown when a game starts.

    Stores the lichess token and serial port (set by MenuScreen) so game
    initialization code can access them.
    """

    white_name = StringProperty("???")
    black_name = StringProperty("???")
    white_time = StringProperty("05:00")
    black_time = StringProperty("05:00")
    
    white_rating = NumericProperty(1500)
    black_rating = NumericProperty(1500)

    white_time_seconds = NumericProperty(10000)
    black_time_seconds = NumericProperty(10000)

    game_id = StringProperty("12345")
    game_status = StringProperty("In Progress")

    active_player = StringProperty("white")  # 'white' or 'black'

    last_move = StringProperty("-")
    last_move_red = BooleanProperty(False)

    blackIsRemote = False
    whiteIsRemote = False

    _timer_event = None
    last_received_turn = None

    def setGameInfo(self, gameInfo):
        """Set initial game information from the workflow manager."""
        self._gameInfo = gameInfo
        self.white_name = gameInfo.wuser
        self.black_name = gameInfo.buser
        self.game_id = gameInfo.gameid
        self.white_rating = gameInfo.wrate
        self.black_rating = gameInfo.brate
        self.blackIsRemote = gameInfo.bremote
        self.whiteIsRemote = gameInfo.wremote

    def on_pre_enter(self):
        """Called before the screen is shown. Prints received values for now."""
        # Start the timer when the screen is shown
        self._timer_event = Clock.schedule_interval(self._decrement_time, 1)

    def on_leave(self):
        """Optional cleanup when leaving the game screen."""
        # Stop the timer when leaving the screen
        if self._timer_event:
            self._timer_event.cancel()
        print("Leaving ChessGameScreen")

    def _decrement_time(self, dt):
        """Decrement the active player's time by 1 second."""
        if self.last_received_turn == "white":
            if self.white_time != "Unlimited":
                self.white_time_seconds = (self.white_time_seconds-1) if self.white_time_seconds > 0 else 0
                self.white_time = self._seconds_to_time_str( self.white_time_seconds)
        elif self.last_received_turn == "black":
            if self.black_time != "Unlimited":
                self.black_time_seconds = (self.black_time_seconds-1) if self.black_time_seconds > 0 else 0
                self.black_time = self._seconds_to_time_str( self.black_time_seconds)

    def _time_str_to_seconds(self, time_str):
        """Convert 'hh:mm:ss' to total seconds."""
        try:
            parts = list(map(int, time_str.split(":")))
            if len(parts) == 3:
                hours, minutes, seconds = parts
            elif len(parts) == 2:
                hours = 0
                minutes, seconds = parts
            else:
                return 0
            return hours * 3600 + minutes * 60 + seconds
        except Exception:
            return 0
        
    def _seconds_to_time_str(self, total_seconds):
        """Convert total seconds to 'hh:mm:ss' format."""
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            return f"{hours:d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

           

    def refresh_state(self, *args, **kwargs):
        """
        Update the game state based on the provided GameState object.
        """
        #if state.status:
        #    print(f"Game status: {state.status.name}")

        obj = args[0] if args else kwargs if kwargs else None

        if isinstance(obj, BoardSync):
            sync: BoardSync = obj

            if sync.aMove:
                self.last_move_red = False
                self.last_move = f"{sync.aMove}"
                self.active_player = self.last_received_turn

        elif isinstance(obj, GameState):
        
            state: GameState = obj

            if state.wtime is not None:
                self.white_time_seconds = state.wtime
                if state.wtime > 604800: # more than a week....
                    self.white_time = "Unlimited"
                else:
                    self.white_time = self._seconds_to_time_str(self.white_time_seconds)

            if state.btime is not None:
                self.black_time_seconds = state.btime
                if state.btime > 604800: # more than a week....
                    self.black_time = "Unlimited"
                else:
                    self.black_time = self._seconds_to_time_str(self.black_time_seconds)
                    

            
            if state.lastMove:
                print(f"Last move: {state.lastMove} Turn: {state.turn}")

                self.last_move = f"{state.lastMove}"

                if state.turn == "white":
                    if self.blackIsRemote:
                        self.last_move_red = True
                        self.active_player = "black"

                    else:
                        self.active_player = state.turn
                    
                else:
                    if self.whiteIsRemote:
                        self.last_move_red = True
                        self.active_player = "white"
                    else:
                        self.active_player = state.turn

                self.last_received_turn = state.turn

                
                    
        else:
            print("Unknown object type:", type(obj))
            return
