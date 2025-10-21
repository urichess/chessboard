from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.clock import Clock

class ChessOnlineUI(BoxLayout):
    player_name = StringProperty("You")
    opponent_name = StringProperty("Opponent")
    player_time = NumericProperty(300)
    opponent_time = NumericProperty(300)
    player_increment = NumericProperty(2)  # seconds
    opponent_increment = NumericProperty(2)
    white_turn = BooleanProperty(True)
    last_move = StringProperty("None")
    full_pgn = StringProperty("")
    game_status = StringProperty("In progress")

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=10, padding=10, **kwargs)

        # Top row: player and opponent info
        top_row = BoxLayout(size_hint_y=0.2, spacing=10)
        self.player_info = Label(text=self.format_player_info(), font_size=20)
        self.opponent_info = Label(text=self.format_opponent_info(), font_size=20)
        top_row.add_widget(self.player_info)
        top_row.add_widget(self.opponent_info)
        self.add_widget(top_row)

        # Middle: game info
        middle_row = BoxLayout(orientation="vertical", size_hint_y=0.5, spacing=10)
        self.turn_label = Label(text=self.format_turn(), font_size=24)
        self.last_move_label = Label(text="Last move: " + self.last_move, font_size=20)
        self.status_label = Label(text="Status: " + self.game_status, font_size=20)

        # PGN scrollable
        self.pgn_view = TextInput(text=self.full_pgn, font_size=16, readonly=True, size_hint_y=0.5)
        middle_row.add_widget(self.turn_label)
        middle_row.add_widget(self.last_move_label)
        middle_row.add_widget(self.status_label)
        middle_row.add_widget(self.pgn_view)
        self.add_widget(middle_row)

        # Update clock every second
        Clock.schedule_interval(self.update_time, 1)

    def format_player_info(self):
        return f"{self.player_name}\nTime: {self.player_time}s (+{self.player_increment})"

    def format_opponent_info(self):
        return f"{self.opponent_name}\nTime: {self.opponent_time}s (+{self.opponent_increment})"

    def format_turn(self):
        return "White to move" if self.white_turn else "Black to move"

    def update_time(self, dt):
        if self.white_turn:
            self.player_time = max(0, self.player_time - 1)
        else:
            self.opponent_time = max(0, self.opponent_time - 1)
        self.player_info.text = self.format_player_info()
        self.opponent_info.text = self.format_opponent_info()
        self.turn_label.text = self.format_turn()

    def new_move(self, move_san):
        self.last_move = move_san
        self.full_pgn += move_san + " "
        # Switch turn
        self.white_turn = not self.white_turn
        # Add increment
        if self.white_turn:
            self.player_time += self.player_increment
        else:
            self.opponent_time += self.opponent_increment
        self.last_move_label.text = "Last move: " + self.last_move
        self.pgn_view.text = self.full_pgn

    def update_status(self, status):
        self.game_status = status
        self.status_label.text = "Status: " + self.game_status

class ChessOnlineApp(App):
    def build(self):
        return ChessOnlineUI()

if __name__ == "__main__":
    ChessOnlineApp().run()

