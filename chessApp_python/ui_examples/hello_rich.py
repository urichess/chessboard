# hello_rich.py

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

# Crear el contenido con estilo
texto = Text("👋 ¡Hola mundo desde Rich!", style="bold green")

# Mostrar en un panel bonito
panel = Panel(texto, title="🌟 Bienvenida", subtitle="powered by rich", border_style="blue")

console.print(panel)

