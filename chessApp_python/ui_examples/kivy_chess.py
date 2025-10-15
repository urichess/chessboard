from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty

KV = '''
<ChessInfoScreen>:
    orientation: 'vertical'
    padding: 20
    spacing: 20

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: '60dp'
        spacing: 20

        BoxLayout:
            orientation: 'vertical'
            Label:
                text: root.my_name
                font_size: '24sp'
                bold: True
            Label:
                text: root.my_timer_str
                font_size: '32sp'

        BoxLayout:
            orientation: 'vertical'
            Label:
                text: root.opponent_name
                font_size: '24sp'
                bold: True
            Label:
                text: root.opponent_timer_str
                font_size: '32sp'

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: '100dp'
        Label:
            text: 'Last Move'
            font_size: '20sp'
            bold: True
        Label:
            text: root.last_move
            font_size: '24sp'

    BoxLayout:
        orientation: 'vertical'
        Label:
            text: 'PGN:'
            font_size: '20sp'
            bold: True
        TextInput:
            text: root.pgn_text
            readonly: True
            size_hint_y: 1
            font_size: '16sp'
            background_color: (1,1,1,1)
'''

class ChessInfoScreen(BoxLayout):
    my_name = StringProperty('Me')
    opponent_name = StringProperty('Opponent')
    my_timer = NumericProperty(5 * 60)
    opponent_timer = NumericProperty(5 * 60)
    my_timer_str = StringProperty('05:00')
    opponent_timer_str = StringProperty('05:00')
    last_move = StringProperty('')
    pgn_text = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_timers, 1)

    def update_timers(self, dt):
        # Simple static countdown simulation (no logic)
        self.my_timer_str = self._format_time(self.my_timer)
        self.opponent_timer_str = self._format_time(self.opponent_timer)

    def _format_time(self, seconds):
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m:02d}:{s:02d}"

class ChessInfoApp(App):
    def build(self):
        Builder.load_string(KV)
        return ChessInfoScreen()

if __name__ == '__main__':
    ChessInfoApp().run()

