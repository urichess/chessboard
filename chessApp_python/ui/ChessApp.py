from kivy.app import App
from ui.MenuScreen import MenuScreen
from ui.ChessGameScreen import ChessGameScreen
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from lib.workflow_manager import WorkflowManager

class ChessApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(ChessGameScreen(name="game"))
        self.workflow = WorkflowManager(sm)
        return sm


if __name__ == "__main__":
    ChessApp().run()

