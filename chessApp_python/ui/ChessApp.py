from kivy.app import App
from ui.MenuScreen import MenuScreen
from ui.ChessGameScreen import ChessGameScreen
from ui.WaitScreen import WaitScreen
from ui.ConfigScreen import ConfigScreen
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from lib.workflow_manager import WorkflowManager
from ui.CreateGameScreen import CreateGameScreen

class ChessApp(App):
    def build(self):
        sm = ScreenManager()
        menu = MenuScreen(name="menu")
        config = ConfigScreen(name="config")
        sm.add_widget(menu)
        sm.add_widget(ChessGameScreen(name="game"))
        sm.add_widget(WaitScreen(name="wait"))
        sm.add_widget(config)
        sm.add_widget(CreateGameScreen(name="create_game"))
        
        self.workflow = WorkflowManager(sm)
        self.workflow.bind_menu_events(menu)
        self.workflow.bind_config_events(config)
        return sm


if __name__ == "__main__":
    ChessApp().run()

