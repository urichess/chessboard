# serial_reader.py

import serial
from board_manager import ChessBoardManager

class SerialChessReader:
    def __init__(self, port, baudrate=115200, position=None):
        self.port = port
        self.baudrate = baudrate
        self.board_manager = ChessBoardManager(position)

    def run(self):
        try:
            with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                print(f"Listening on {self.port} at {self.baudrate} baud...\n")
                self.board_manager.wait_for_position(ser)
                while True:
                    line = ser.readline().decode(errors='ignore').strip()
                    if not line:
                        continue
                    board_matrix = self.board_manager.parse_board_line(line)
                    if board_matrix:
                        self.board_manager.print_detected_board(board_matrix)
        except serial.SerialException as e:
            print(f"Serial error: {e}")

