# board_manager.py

import time
import chess
from constants import INITIAL_POSITION_PIECES

class ChessBoardManager:
    def __init__(self, target_position=None):
        self.target_position = target_position or INITIAL_POSITION_PIECES
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

            all_correct = all(
                ((row, col) in self.target_position) == (board_matrix[row][col] == 1)
                for row in range(8) for col in range(8)
            )

            if all_correct:
                print("✅ All pieces correctly placed. The game can start!\n")
                return

            time.sleep(1)

