from PIL import Image, ImageDraw, ImageFont
import pygame
import sys

# Configura el tamaño de la pantalla ILI9341
WIDTH, HEIGHT = 240, 320

# Inicializa Pygame
pygame.init()
pantalla = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Emulador ILI9341")

# Crea una imagen Pillow para dibujar
imagen = Image.new("RGB", (WIDTH, HEIGHT), "black")
dibujo = ImageDraw.Draw(imagen)
fuente = ImageFont.load_default()

# Ejemplo de dibujo
dibujo.rectangle((0, 0, WIDTH, HEIGHT), fill="blue")
dibujo.text((10, 10), "Hola ILI9341", font=fuente, fill="white")

# Bucle de visualización
reloj = pygame.time.Clock()
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Convierte la imagen Pillow a formato Pygame
    modo = imagen.mode
    tam = imagen.size
    datos = imagen.tobytes()
    imagen_pygame = pygame.image.fromstring(datos, tam, modo)
    pantalla.blit(imagen_pygame, (0, 0))
    pygame.display.flip()
    reloj.tick(30)

