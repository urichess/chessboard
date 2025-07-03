
import chess
import sys

def parse_board_line(board_line):
    if not board_line.startswith("BOARD:"):
        raise ValueError("Line must start with 'BOARD:'")

    hex_parts = board_line[6:].split("-")
    if len(hex_parts) != 8:
        raise ValueError("Expected 8 bytes")

    board = chess.Board(None)  # start with empty board

    for rank in range(8):  # rank 1 (bottom) to 8 (top)
        byte = int(hex_parts[rank], 16)
        for file in range(8):
            bit = (byte >> (7 - file)) & 1
            if bit:
                square = chess.square(file, rank)
                board.set_piece_at(square, chess.Piece(chess.PAWN, chess.WHITE))

    return board

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python print_sensor_board.py 'BOARD:FF-FF-00-00-00-00-FF-FF'")
        sys.exit(1)

    board_line = sys.argv[1]
    board = parse_board_line(board_line)
    print(board)

