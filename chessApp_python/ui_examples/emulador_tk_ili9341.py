from tkinter import Tk, Canvas
from PIL import Image, ImageTk, ImageDraw, ImageFont

# Tamaño del display ILI9341
WIDTH, HEIGHT = 240, 320

# Crear imagen con Pillow
imagen = Image.new("RGB", (WIDTH, HEIGHT), "black")
dibujo = ImageDraw.Draw(imagen)
fuente = ImageFont.load_default()

# Dibujar botón de prueba
boton_area = (60, 100, 180, 140)
dibujo.rectangle(boton_area, fill="red")
dibujo.text((70, 110), "Presionar", font=fuente, fill="white")

# Crear ventana
root = Tk()
root.title("Emulador ILI9341")

# Convertir a formato que Tkinter entiende
tk_imagen = ImageTk.PhotoImage(imagen)

# Canvas para mostrar imagen
canvas = Canvas(root, width=WIDTH, height=HEIGHT)
canvas.pack()
canvas_imagen = canvas.create_image(0, 0, anchor="nw", image=tk_imagen)

# Función que simula toque
def on_click(event):
    x, y = event.x, event.y
    print(f"Toque simulado en: {x}, {y}")
    if boton_area[0] <= x <= boton_area[2] and boton_area[1] <= y <= boton_area[3]:
        print("Botón presionado")
        dibujo.rectangle(boton_area, fill="green")
        dibujo.text((70, 110), "¡OK!", font=fuente, fill="black")
        actualizar()

# Actualiza imagen en ventana
def actualizar():
    global tk_imagen
    tk_imagen = ImageTk.PhotoImage(imagen)
    canvas.itemconfig(canvas_imagen, image=tk_imagen)

# Detecta clics del mouse
canvas.bind("<Button-1>", on_click)

# Iniciar interfaz
root.mainloop()

