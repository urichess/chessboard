from kivy.app import App
from ui.MenuScreen import MenuScreen
from ui.ChessGameScreen import ChessGameScreen
from kivy.uix.screenmanager import ScreenManager, SlideTransition

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

class ChessApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(ChessGameScreen(name="game"))
        self.workflow = WorkflowManager(sm)
        return sm


if __name__ == "__main__":
    ChessApp().run()

