import time
import threading
from core.calculator import Calculator


class WorkflowManager:
    """Controls the app's workflow logic, independent from any UI framework."""

    def __init__(self):
        self._listeners = {}
        self.calculator = Calculator()
        self.state = {
            "a": None,
            "b": None,
            "result": None,
            "progress": 0,
            "status": "Idle"
        }

    # --- Event system ----------------------------------------------------
    def on(self, event, callback):
        """Subscribe to workflow events (status, progress, state_changed, etc.)"""
        self._listeners.setdefault(event, []).append(callback)

    def _emit(self, event, *args, **kwargs):
        for cb in self._listeners.get(event, []):
            cb(*args, **kwargs)

    # --- Workflow logic --------------------------------------------------
    def set_inputs(self, a, b):
        self.state["a"], self.state["b"] = a, b
        self._emit("state_changed", dict(self.state))

    def start(self, async_mode=True):
        if async_mode:
            t = threading.Thread(target=self._workflow_async, daemon=True)
            t.start()
        else:
            self._workflow_sync()

    def _workflow_sync(self):
        """Simplified sync version."""
        self._set_status("Running (sync)")
        a, b = self.state["a"], self.state["b"]
        self.state["result"] = self.calculator.add(a, b)
        self._emit("state_changed", dict(self.state))
        self._set_status("Done")

    def _workflow_async(self):
        """Simulated long-running async workflow with progress updates."""
        self._set_status("Running (async)")
        self.state["progress"] = 0

        # Example workflow: progress updates, then calculation
        for i in range(1, 11):
            time.sleep(0.25)
            self.state["progress"] = i * 10
            self._emit("progress", self.state["progress"])

        a, b = self.state["a"], self.state["b"]
        self.state["result"] = self.calculator.add(a, b)
        self._emit("state_changed", dict(self.state))
        self._set_status("Done")

    # --- Helpers ---------------------------------------------------------
    def _set_status(self, msg):
        self.state["status"] = msg
        self._emit("status", msg)

