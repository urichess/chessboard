# chessboard

tests of chessboard using arduino + zephyr


Interesting links

Proyectos y tecnologías clave que te pueden ayudar
1. lichess-bot

https://github.com/lichess-bot-devs/lichess-bot

Un bot que se conecta a la API de Lichess y puede jugar partidas automáticamente.

Puedes modificarlo para que, en lugar de usar un motor de ajedrez, se comunique con tu hardware.

Es ideal como punto de partida para jugar partidas en Lichess a través de tu propio programa.

2. PySerial

https://pyserial.readthedocs.io/en/latest/pyserial.html#overview
Para comunicarte con tu tablero por USB (si usas un puerto serie virtual tipo /dev/ttyUSB0).

Puedes leer movimientos desde tu tablero y enviarle información como el movimiento del oponente.

3. Python-Chess
https://python-chess.readthedocs.io/en/latest/#
Excelente librería para manejar lógica de ajedrez (validar jugadas, FENs, PGNs).

Puedes usarla para comparar el estado del juego local con el de Lichess y traducir movimientos.


