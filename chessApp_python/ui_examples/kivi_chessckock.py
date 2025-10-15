from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty, StringProperty

class ChessClock(BoxLayout):
    white_time = NumericProperty(300)
    black_time = NumericProperty(300)
    white_turn = BooleanProperty(True)
    running = BooleanProperty(False)
    last_move = StringProperty("None")

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=20, padding=20, **kwargs)
        # Top horizontal clock layout
        self.clock_layout = BoxLayout(spacing=10, size_hint_y=0.6)
        self.white_label = Label(text=self.format_time(self.white_time), font_size=64, color=(0,0,0,1))
        self.black_label = Label(text=self.format_time(self.black_time), font_size=64, color=(1,1,1,1))
        self.clock_layout.add_widget(self.black_label)
        self.clock_layout.add_widget(self.white_label)
        self.add_widget(self.clock_layout)

        # Info label
        self.last_move_label = Label(text="Last move: " + self.last_move, font_size=20, size_hint_y=0.1)
        self.add_widget(self.last_move_label)

        # Buttons
        btn_layout = BoxLayout(spacing=10, size_hint_y=0.3)
        start_btn = Button(text="Start / Pause", font_size=22, on_release=lambda x: self.toggle_clock())
        switch_btn = Button(text="Switch Turn", font_size=22, on_release=lambda x: self.switch_turn())
        reset_btn = Button(text="Reset", font_size=22, on_release=lambda x: self.reset_clock())
        btn_layout.add_widget(start_btn)
        btn_layout.add_widget(switch_btn)
        btn_layout.add_widget(reset_btn)
        self.add_widget(btn_layout)

        Clock.schedule_interval(self.update_time, 1)
        self.update_colors()

    def format_time(self, seconds):
        m, s = divmod(int(seconds), 60)
        return f"{m:02d}:{s:02d}"

    def update_time(self, dt):
        if not self.running:
            return
        if self.white_turn:
            self.white_time = max(0, self.white_time - 1)
        else:
            self.black_time = max(0, self.black_time - 1)
        self.white_label.text = self.format_time(self.white_time)
        self.black_label.text = self.format_time(self.black_time)

    def toggle_clock(self):
        self.running = not self.running

    def switch_turn(self):
        if not self.running:
            return
        self.white_turn = not self.white_turn
        self.last_move = "White" if not self.white_turn else "Black"
        self.last_move_label.text = "Last move: " + self.last_move
        self.update_colors()

    def reset_clock(self):
        self.white_time = 300
        self.black_time = 300
        self.white_turn = True
        self.running = False
        self.last_move = "None"
        self.last_move_label.text = "Last move: None"
        self.white_label.text = self.format_time(self.white_time)
        self.black_label.text = self.format_time(self.black_time)
        self.update_colors()

    def update_colors(self):
        # Active clock highlighted
        if self.white_turn:
            self.white_label.color = (0, 0, 0, 1)
            self.white_label.canvas.before.clear()
            with self.white_label.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0.9, 0.9, 0.5, 1)
                Rectangle(pos=self.white_label.pos, size=self.white_label.size)
            self.black_label.color = (1, 1, 1, 1)
        else:
            self.black_label.color = (1, 1, 1, 1)
            self.black_label.canvas.before.clear()
            with self.black_label.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0.9, 0.6, 0.2, 1)
                Rectangle(pos=self.black_label.pos, size=self.black_label.size)
            self.white_label.color = (0, 0, 0, 1)

class ChessClockApp(App):
    def build(self):
        return ChessClock()

if __name__ == "__main__":
    ChessClockApp().run()

