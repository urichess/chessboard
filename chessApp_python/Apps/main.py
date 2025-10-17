from kivy.app import App
from ui.chessui import ChessUI


class ChessApp(App):
    def build(self):
        return ChessUI()


if __name__ == "__main__":
    ChessApp().run()

