from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import time
import os

def mostrar_estado(jugada, turno, tiempo_blancas, tiempo_negras, estado):
    console = Console()
    table = Table(title="Estado de la Partida", expand=True)

    table.add_column("Elemento", justify="left", style="cyan", no_wrap=True)
    table.add_column("Valor", style="bold")

    table.add_row("Última jugada", f"[red]{jugada}[/red]")
    table.add_row("Turno", f"[green]{turno}[/green]")
    table.add_row("Tiempo Blancas", f"[white]{tiempo_blancas}[/white]")
    table.add_row("Tiempo Negras", f"[white]{tiempo_negras}[/white]")
    table.add_row("Estado", f"[magenta]{estado.upper()}[/magenta]")

    console.clear()
    console.print(Panel(table, title="⏳ Chess Monitor", border_style="bright_blue"))

# Simulación simple con actualización de reloj
def run_simulacion():
    t_white = 60  # segundos
    t_black = 58
    jugadas = ['e4', 'c5', 'Nf3', 'd6', 'd4']
    turno = "Blancas"
    estado = "En juego"

    for move in jugadas:
        for i in range(3):  # Simula 3 segundos por turno
            tiempo_b = time.strftime('%M:%S', time.gmtime(t_white))
            tiempo_n = time.strftime('%M:%S', time.gmtime(t_black))

            mostrar_estado(
                jugada=move,
                turno=turno,
                tiempo_blancas=tiempo_b,
                tiempo_negras=tiempo_n,
                estado=estado
            )

            time.sleep(1)
            if turno == "Blancas":
                t_white -= 1
            else:
                t_black -= 1

        turno = "Negras" if turno == "Blancas" else "Blancas"

    # Muestra final
    mostrar_estado(
        jugada=jugadas[-1],
        turno="Fin",
        tiempo_blancas=time.strftime('%M:%S', time.gmtime(t_white)),
        tiempo_negras=time.strftime('%M:%S', time.gmtime(t_black)),
        estado="Finalizado"
    )

if __name__ == "__main__":
    run_simulacion()

