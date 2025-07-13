import tkinter as tk

# Crear ventana principal
root = tk.Tk()
root.title("Hello World con Tkinter")

# Crear una etiqueta (label) con texto
label = tk.Label(root, text="Hello World!")
label.pack(padx=20, pady=20)  # Empaqueta la etiqueta con algo de espacio alrededor

# Iniciar el bucle principal de la GUI
root.mainloop()

