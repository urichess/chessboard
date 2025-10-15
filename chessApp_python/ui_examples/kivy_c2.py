from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
import random

# Fondo negro
#Window.clearcolor = (0, 0, 0, 1)
#Fondo gris
Window.clearcolor = (0.83, 0.83, 0.83, 1)


class ChessMonitor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=15, **kwargs)

        # Datos iniciales
        self.user_blancas = "Alice"
        self.user_negras = "Bob"
        self.turno = "Blancas"
        self.ultima_jugada = "-"
        self.tiempo_blancas = 300
        self.tiempo_negras = 300
        self.estado = "En juego"
        self.identificador = "ID: 12345ABC"

        # --- Última jugada ---
        self.lbl_titulo_jugada = Label(
            text="Última jugada:",
            font_size="28sp",
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=40
        )
        self.lbl_jugada = Label(
            text=self.ultima_jugada,
            font_size="70sp",
            bold=True,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=100
        )
        self.add_widget(self.lbl_titulo_jugada)
        self.add_widget(self.lbl_jugada)

        # --- Jugadores y tiempos ---
        frame_jugadores = GridLayout(cols=2, size_hint_y=None, height=150)

        # Blancas
        frame_blancas = BoxLayout(orientation="vertical", padding=[10, 0])
        self.lbl_user_b = Label(
            text=f"Blancas: {self.user_blancas}",
            font_size="22sp",
            color=(0, 0, 0, 1),
            halign="left"
        )
        self.lbl_tiempo_b = Label(
            text="05:00",
            font_size="60sp",
            bold=True,
            color=(0, 1, 0, 1)
        )
        frame_blancas.add_widget(self.lbl_user_b)
        frame_blancas.add_widget(self.lbl_tiempo_b)

        # Negras
        frame_negras = BoxLayout(orientation="vertical", padding=[10, 0])
        self.lbl_user_n = Label(
            text=f"Negras: {self.user_negras}",
            font_size="22sp",
            color=(0, 0, 0, 1),
            halign="right"
        )
        self.lbl_tiempo_n = Label(
            text="05:00",
            font_size="60sp",
            bold=True,
            color=(0.5, 0.5, 0.5, 1)
        )
        frame_negras.add_widget(self.lbl_user_n)
        frame_negras.add_widget(self.lbl_tiempo_n)

        frame_jugadores.add_widget(frame_blancas)
        frame_jugadores.add_widget(frame_negras)
        self.add_widget(frame_jugadores)

        # --- Turno ---
        self.lbl_turno = Label(
            text="Turno: Blancas",
            font_size="30sp",
            bold=True,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=50
        )
        self.add_widget(self.lbl_turno)

        # --- Estado e identificador ---
        frame_estado = GridLayout(cols=2, size_hint_y=None, height=40, padding=[10, 0])
        self.lbl_estado = Label(
            text=f"Estado: {self.estado}",
            font_size="18sp",
            italic=True,
            color=(0, 0, 0, 1),
            halign="left"
        )
        self.lbl_id = Label(
            text=self.identificador,
            font_size="18sp",
            italic=True,
            color=(0, 0, 0, 1),
            halign="right"
        )
        frame_estado.add_widget(self.lbl_estado)
        frame_estado.add_widget(self.lbl_id)
        self.add_widget(frame_estado)

        # --- Botón simular ---
        self.btn_jugar = Button(
            text="Simular jugada",
            size_hint_y=None,
            height=60,
            font_size="22sp",
            background_color=(0.3, 0.3, 0.3, 1),
            color=(0, 0, 0, 1),
            on_press=self.simular_jugada
        )
        self.add_widget(self.btn_jugar)

        # --- Actualización del reloj ---
        Clock.schedule_interval(self.update_clock, 1)

    def update_clock(self, dt):
        if self.turno == "Blancas":
            self.tiempo_blancas = max(0, self.tiempo_blancas - 1)
        else:
            self.tiempo_negras = max(0, self.tiempo_negras - 1)

        self.lbl_tiempo_b.text = self.formato_tiempo(self.tiempo_blancas)
        self.lbl_tiempo_n.text = self.formato_tiempo(self.tiempo_negras)

        # Colores según el turno
        if self.turno == "Blancas":

#            self.lbl_tiempo_b.color = (0, 1, 0, 1)
            self.lbl_tiempo_b.color = (0, 0.6, 0, 1)
            self.lbl_tiempo_n.color = (0.5, 0.5, 0.5, 1)
        else:
            #self.lbl_tiempo_n.color = (0, 1, 0, 1)
            self.lbl_tiempo_n.color = (0, 0.6, 0, 1)
            self.lbl_tiempo_b.color = (0.5, 0.5, 0.5, 1)

    def formato_tiempo(self, segundos):
        m, s = divmod(segundos, 60)
        return f"{m:02d}:{s:02d}"

    def simular_jugada(self, instance):
        jugadas = ["e4", "c5", "Nf3", "d6", "d4", "cxd4", "Nxd4", "Bb5", "Nc6"]
        nueva_jugada = random.choice(jugadas)
        self.lbl_jugada.text = nueva_jugada  # ✅ ahora se actualiza bien

        self.turno = "Negras" if self.turno == "Blancas" else "Blancas"
        self.lbl_turno.text = f"Turno: {self.turno}"


class ChessApp(App):
    def build(self):
        self.title = "Chess Monitor Visual"
        return ChessMonitor()


if __name__ == "__main__":
    ChessApp().run()

