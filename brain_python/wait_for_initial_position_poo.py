import serial
import chess
import argparse
import time

# Lowercase = black, Uppercase = white
INITIAL_POSITION_PIECES = {
    # Black
    (0, 0): 'r', (0, 1): 'n', (0, 2): 'b', (0, 3): 'q',
    (0, 4): 'k', (0, 5): 'b', (0, 6): 'n', (0, 7): 'r',
    (1, 0): 'p', (1, 1): 'p', (1, 2): 'p', (1, 3): 'p',
    (1, 4): 'p', (1, 5): 'p', (1, 6): 'p', (1, 7): 'p',
    # White
    (6, 0): 'P', (6, 1): 'P', (6, 2): 'P', (6, 3): 'P',
    (6, 4): 'P', (6, 5): 'P', (6, 6): 'P', (6, 7): 'P',
    (7, 0): 'R', (7, 1): 'N', (7, 2): 'B', (7, 3): 'Q',
    (7, 4): 'K', (7, 5): 'B', (7, 6): 'N', (7, 7): 'R',
}

class ChessBoardManager:
    def __init__(self, target_position):
        self.target_position = target_position
        self.occupied = set()

    @staticmethod
    def parse_board_line(line):
        if not line.startswith("BOARD:"):
            return None
        try:
            hex_part = line.strip().split("BOARD:")[1]
            hex_bytes = hex_part.split('-')
            if len(hex_bytes) != 8:
                return None
            board_matrix = []
            for byte_str in hex_bytes:
                byte = int(byte_str, 16)
                row = [(byte >> (7 - i)) & 1 for i in range(8)]
                board_matrix.append(row)
            return board_matrix
        except Exception as e:
            print(f"Error parsing line: {e}")
            return None

    def print_target_position(self):
        board = chess.Board.empty()
        for (row, col), piece_symbol in self.target_position.items():
            square = chess.square(col, 7 - row)
            color = chess.WHITE if piece_symbol.isupper() else chess.BLACK
            piece_type = chess.PIECE_SYMBOLS.index(piece_symbol.lower())
            board.set_piece_at(square, chess.Piece(piece_type, color))
        print("Target position:")
        print(board.unicode(empty_square=" ", borders=True))
        print()

    def print_detected_board(self, board_matrix):
        board = chess.Board.empty()
        for (row, col), piece_symbol in self.target_position.items():
            if board_matrix[row][col] == 1:
                square = chess.square(col, 7 - row)
                color = chess.WHITE if piece_symbol.isupper() else chess.BLACK
                piece_type = chess.PIECE_SYMBOLS.index(piece_symbol.lower())
                board.set_piece_at(square, chess.Piece(piece_type, color))
        print(board.unicode(empty_square=" ", borders=True))
        print()

    def wait_for_position(self, ser, message="Place pieces as shown above"):
        print(message)
        self.print_target_position()

        while True:
            line = ser.readline().decode(errors='ignore').strip()
            if not line:
                continue

            board_matrix = self.parse_board_line(line)
            if not board_matrix:
                continue

            changes = False
            for (row, col), piece in self.target_position.items():
                detected = board_matrix[row][col] == 1
                if detected and (row, col) not in self.occupied:
                    print(f"Detected {piece} on {chess.square_name(chess.square(col, 7 - row))}")
                    self.occupied.add((row, col))
                    changes = True
                elif not detected and (row, col) in self.occupied:
                    print(f"Removed {piece} from {chess.square_name(chess.square(col, 7 - row))}")
                    self.occupied.remove((row, col))
                    changes = True

            if changes:
                print(f"Detected correct placements: {len(self.occupied)}/{len(self.target_position)}\n")

            # Check that all expected are present, and no extra pieces
            all_correct = True
            for row in range(8):
                for col in range(8):
                    expected = (row, col) in self.target_position
                    detected = board_matrix[row][col] == 1
                    if expected != detected:
                        all_correct = False
                        break
                if not all_correct:
                    break

            if all_correct:
                print("✅ All pieces correctly placed. The game can start!\n")
                return

            time.sleep(1)

class SerialChessReader:
    def __init__(self, port, baudrate=115200, target_position=None):
        self.port = port
        self.baudrate = baudrate
        self.target_position = target_position or INITIAL_POSITION_PIECES
        self.board_manager = ChessBoardManager(self.target_position)

    def run(self):
        try:
            with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                print(f"Listening on {self.port} at {self.baudrate} baud...\n")

                self.board_manager.wait_for_position(
                    ser,
                    message="Please set up the board to the initial position:"
                )

                while True:
                    line = ser.readline().decode(errors='ignore').strip()
                    if not line:
                        continue
                    board_matrix = self.board_manager.parse_board_line(line)
                    if board_matrix:
                        self.board_manager.print_detected_board(board_matrix)

        except serial.SerialException as e:
            print(f"Serial error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Chessboard serial reader")
    parser.add_argument("--port", "-p", required=True, help="Serial port device (e.g., /dev/ttyUSB0 or COM3)")
    parser.add_argument("--baudrate", "-b", type=int, default=115200, help="Serial port baud rate (default: 115200)")
    args = parser.parse_args()

    client = SerialChessReader(args.port, args.baudrate)
    client.run()

if __name__ == "__main__":
    main()

