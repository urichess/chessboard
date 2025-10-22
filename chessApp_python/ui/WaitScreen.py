import json
import os
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.app import App
from kivy.properties import StringProperty

class WaitScreen(Screen):
    """A simple screen showing a waiting message."""
    message = StringProperty("Please wait...")

    def on_pre_enter(self):
        # You can perform setup or start an animation here if needed
        pass