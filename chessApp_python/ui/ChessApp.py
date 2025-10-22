from kivy.app import App
from ui.MenuScreen import MenuScreen
from ui.ChessGameScreen import ChessGameScreen
from ui.WaitScreen import WaitScreen
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from lib.workflow_manager import WorkflowManager

class ChessApp(App):
    def build(self):
        sm = ScreenManager()
        menu = MenuScreen(name="menu")
        sm.add_widget(menu)
        sm.add_widget(ChessGameScreen(name="game"))
        sm.add_widget(WaitScreen(name="wait"))


        
        self.workflow = WorkflowManager(sm)
        self.workflow.bind_menu_events(menu)
        return sm


if __name__ == "__main__":
    ChessApp().run()

