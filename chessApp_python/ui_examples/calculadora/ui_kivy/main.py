from kivy.app import App
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import mainthread
from core.workflow import WorkflowManager


class CalculatorUI(BoxLayout):
    status = StringProperty("Idle")
    result = StringProperty("No result")
    progress = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.workflow = WorkflowManager()

        # Subscribe to workflow events
        self.workflow.on("status", self._on_status)
        self.workflow.on("state_changed", self._on_state_changed)
        self.workflow.on("progress", self._on_progress)

    def on_start_sync(self):
        a = float(self.ids.input_a.text or 0)
        b = float(self.ids.input_b.text or 0)
        self.workflow.set_inputs(a, b)
        self.workflow.start(async_mode=False)

    def on_start_async(self):
        a = float(self.ids.input_a.text or 0)
        b = float(self.ids.input_b.text or 0)
        self.workflow.set_inputs(a, b)
        self.workflow.start(async_mode=True)

    # --- Event handlers (safe for UI thread) -----------------------------
    @mainthread
    def _on_status(self, msg):
        self.status = msg

    @mainthread
    def _on_state_changed(self, state):
        self.result = str(state.get("result", "None"))

    @mainthread
    def _on_progress(self, value):
        self.progress = value


class CalculatorApp(App):
    def build(self):
        return CalculatorUI()


if __name__ == "__main__":
    CalculatorApp().run()

