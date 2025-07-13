from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
import time

console = Console()

def render_estado(jugada, turno, tiempo_blancas, tiempo_negras, estado):
    table = Table.grid(expand=True)
    table.add_column(justify="right", style="cyan", no_wrap=True)
    table.add_column(width=4)  # columna vacía para espacio
    table.add_column(justify="left", style="bold")

    table.add_row("Última jugada", "", f"[red]{jugada}[/red]")
    table.add_row("Turno", "", f"[green]{turno}[/green]")
    table.add_row("Tiempo Blancas", "", f"[white]{tiempo_blancas}[/white]")
    table.add_row("Tiempo Negras", "", f"[white]{tiempo_negras}[/white]")
    table.add_row("Estado", "", f"[magenta]{estado.upper()}[/magenta]")

    return Panel(table, title="⏳ Chess Monitor", border_style="bright_blue")


def run_simulacion():
    t_white = 60
    t_black = 58
    jugadas = ['e4', 'c5', 'Nf3', 'd6', 'd4']
    turno = "Blancas"
    estado = "En juego"
    current_move = ""

    with Live(render_estado(current_move, turno, "00:00", "00:00", estado), refresh_per_second=4, screen=True) as live:
        for move in jugadas:
            current_move = move
            for _ in range(3):
                tiempo_b = time.strftime('%M:%S', time.gmtime(t_white))
                tiempo_n = time.strftime('%M:%S', time.gmtime(t_black))

                live.update(render_estado(current_move, turno, tiempo_b, tiempo_n, estado))
                time.sleep(1)

                if turno == "Blancas":
                    t_white -= 1
                else:
                    t_black -= 1

            turno = "Negras" if turno == "Blancas" else "Blancas"

        estado = "Finalizado"
        tiempo_b = time.strftime('%M:%S', time.gmtime(t_white))
        tiempo_n = time.strftime('%M:%S', time.gmtime(t_black))
        live.update(render_estado(current_move, "Fin", tiempo_b, tiempo_n, estado))

if __name__ == "__main__":
    run_simulacion()

