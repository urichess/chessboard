from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock
from lib.messages import GameState

class ChessGameScreen(Screen):
    """A simple screen shown when a game starts.

    Stores the lichess token and serial port (set by MenuScreen) so game
    initialization code can access them.
    """

    white_name = StringProperty("???")
    black_name = StringProperty("???")
    white_time = StringProperty("05:00")
    black_time = StringProperty("05:00")
    white_last_move = StringProperty("-")
    black_last_move = StringProperty("-")

    active_player = StringProperty("white")  # 'white' or 'black'

    _timer_event = None

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
        if self.active_player == "white":
            self.white_time = self._decrement_time_str(self.white_time)
        elif self.active_player == "black":
            self.black_time = self._decrement_time_str(self.black_time)

    def _decrement_time_str(self, time_str):
        """Convert 'mm:ss' to seconds, decrement, and format back."""
        try:
            minutes, seconds = map(int, time_str.split(":"))
            total_seconds = minutes * 60 + seconds
            total_seconds = max(0, total_seconds - 1)
            new_minutes = total_seconds // 60
            new_seconds = total_seconds % 60
            return f"{new_minutes:02d}:{new_seconds:02d}"
        except Exception:
            return time_str


    def refresh_state(self, *args, **kwargs):
        """
        Update the game state based on the provided GameState object.
        """
        #if state.status:
        #    print(f"Game status: {state.status.name}")

        obj = args[0] if args else kwargs if kwargs else None

        if not isinstance(obj, GameState):
            print("⚠️ No llegó GameState, llegó:", type(obj))
            return
        
        state: GameState = obj

        if state.wtime is not None:
            if state.wtime == 2147483647:
                self.white_time = "Unlimited"
            else:
                hours = state.wtime // 3600
                minutes = (state.wtime % 3600) // 60
                seconds = state.wtime % 60
                if hours > 0:
                    self.white_time = f"{hours:d}:{minutes:02d}:{seconds:02d}"
                else:
                    self.white_time = f"{minutes:02d}:{seconds:02d}"

        if state.btime is not None:
            if state.btime == 2147483647:
                self.black_time = "Unlimited"
            else:
                hours = state.btime // 3600
                minutes = (state.btime % 3600) // 60
                seconds = state.btime % 60
                if hours > 0:
                    self.black_time = f"{hours:d}:{minutes:02d}:{seconds:02d}"
                else:
                    self.black_time = f"{minutes:02d}:{seconds:02d}"


        
        if state.lastMove:
            print(f"Last move: {state.lastMove} Turn: {state.turn}")

            if state.turn == "black":
                self.white_last_move = state.lastMove
                self.black_last_move = ""
            else:
                self.white_last_move = ""
                self.black_last_move = state.lastMove
