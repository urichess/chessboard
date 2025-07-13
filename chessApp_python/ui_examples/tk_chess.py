import tkinter as tk
from tkinter import ttk
import random

class ChessMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chess Monitor Visual")
        self.geometry("400x320")  # Más alto para que quepa todo bien
        self.resizable(False, False)
        
        self.user_blancas = "Alice"
        self.user_negras = "Bob"
        
        self.turno = "Blancas"
        self.ultima_jugada = "-"
        self.tiempo_blancas = 300  # 5 minutos
        self.tiempo_negras = 300
        
        self.estado = "En juego"
        self.identificador = "ID: 12345ABC"
        
        self.create_widgets()
        self.update_clock()
        
    def create_widgets(self):
        frame_ultima = ttk.Frame(self)
        frame_ultima.pack(pady=10)

        lbl_texto = ttk.Label(frame_ultima, text="Última jugada:", font=("Arial", 14))
        lbl_texto.pack(side="left")

        self.lbl_jugada = ttk.Label(frame_ultima, text="-", font=("Arial", 40, "bold"), foreground="black")
        self.lbl_jugada.pack(side="left", padx=(10, 0))
        
        frame_jugadores = ttk.Frame(self)
        frame_jugadores.pack(fill="x", padx=20, pady=5)
        
        frame_blancas = ttk.Frame(frame_jugadores)
        frame_blancas.pack(side="left", fill="x", expand=True)
        self.lbl_user_b = ttk.Label(frame_blancas, text=f"Blancas: {self.user_blancas}", font=("Arial", 14))
        self.lbl_user_b.pack(anchor="w")
        self.lbl_tiempo_b = ttk.Label(frame_blancas, text="05:00", font=("Arial", 40, "bold"))
        self.lbl_tiempo_b.pack(anchor="w")
        
        frame_negras = ttk.Frame(frame_jugadores)
        frame_negras.pack(side="right", fill="x", expand=True)
        self.lbl_user_n = ttk.Label(frame_negras, text=f"Negras: {self.user_negras}", font=("Arial", 14))
        self.lbl_user_n.pack(anchor="e")
        self.lbl_tiempo_n = ttk.Label(frame_negras, text="05:00", font=("Arial", 40, "bold"))
        self.lbl_tiempo_n.pack(anchor="e")
        
        self.lbl_turno = ttk.Label(self, text="Turno: Blancas", font=("Arial", 16, "bold"))
        self.lbl_turno.pack(pady=8)
        
        frame_estado = ttk.Frame(self)
        frame_estado.pack(pady=5, fill="x", padx=20)
        self.lbl_estado = ttk.Label(frame_estado, text=f"Estado: {self.estado}", font=("Arial", 12, "italic"))
        self.lbl_estado.pack(side="left", padx=10)
        self.lbl_id = ttk.Label(frame_estado, text=self.identificador, font=("Arial", 12, "italic"))
        self.lbl_id.pack(side="right", padx=10)
        
        self.btn_jugar = ttk.Button(self, text="Simular jugada", command=self.simular_jugada)
        self.btn_jugar.pack(pady=15, fill='x', padx=40)  # Ahora el botón es ancho y separado
        
    def update_clock(self):
        if self.turno == "Blancas":
            self.tiempo_blancas = max(0, self.tiempo_blancas - 1)
        else:
            self.tiempo_negras = max(0, self.tiempo_negras - 1)
        
        self.lbl_tiempo_b.config(text=self.formato_tiempo(self.tiempo_blancas))
        self.lbl_tiempo_n.config(text=self.formato_tiempo(self.tiempo_negras))
        
        if self.turno == "Blancas":
            self.lbl_tiempo_b.config(foreground="green")
            self.lbl_tiempo_n.config(foreground="grey")
        else:
            self.lbl_tiempo_n.config(foreground="green")
            self.lbl_tiempo_b.config(foreground="grey")
        
        self.after(1000, self.update_clock)
        
    def formato_tiempo(self, segundos):
        m, s = divmod(segundos, 60)
        return f"{m:02d}:{s:02d}"
    
    def simular_jugada(self):
        jugadas = ["e4", "c5", "Nf3", "d6", "d4", "cxd4", "Nxd4"]
        nueva_jugada = random.choice(jugadas)
        self.lbl_jugada.config(text=nueva_jugada)
        
        self.turno = "Negras" if self.turno == "Blancas" else "Blancas"
        self.lbl_turno.config(text=f"Turno: {self.turno}")

if __name__ == "__main__":
    app = ChessMonitor()
    app.mainloop()

