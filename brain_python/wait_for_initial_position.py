
import serial
import chess
import argparse
import time

# Lowercase = black, Uppercase = white
INITIAL_POSITION_PIECES = {
    # Black pieces
    (0, 0): 'r', (0, 1): 'n', (0, 2): 'b', (0, 3): 'q',
    (0, 4): 'k', (0, 5): 'b', (0, 6): 'n', (0, 7): 'r',
    (1, 0): 'p', (1, 1): 'p', (1, 2): 'p', (1, 3): 'p',
    (1, 4): 'p', (1, 5): 'p', (1, 6): 'p', (1, 7): 'p',
    # White pieces
    (6, 0): 'P', (6, 1): 'P', (6, 2): 'P', (6, 3): 'P',
    (6, 4): 'P', (6, 5): 'P', (6, 6): 'P', (6, 7): 'P',
    (7, 0): 'R', (7, 1): 'N', (7, 2): 'B', (7, 3): 'Q',
    (7, 4): 'K', (7, 5): 'B', (7, 6): 'N', (7, 7): 'R',
}

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

def print_position(position_dict):
    board = chess.Board.empty()
    for (row, col), piece_symbol in position_dict.items():
        square = chess.square(col, 7 - row)
        color = chess.WHITE if piece_symbol.isupper() else chess.BLACK
        piece_type = chess.PIECE_SYMBOLS.index(piece_symbol.lower())
        board.set_piece_at(square, chess.Piece(piece_type, color))
    print("Target position:")
    print(board.unicode(empty_square=" ", borders=True))
    print()

def print_board_with_chess(board_matrix, position_dict):
    if not board_matrix:
        return
    board = chess.Board.empty()
    for (row, col), piece_symbol in position_dict.items():
        square = chess.square(col, 7 - row)
        if board_matrix[row][col] == 1:
            color = chess.WHITE if piece_symbol.isupper() else chess.BLACK
            piece_type = chess.PIECE_SYMBOLS.index(piece_symbol.lower())
            board.set_piece_at(square, chess.Piece(piece_type, color))
    print(board.unicode(empty_square=" ", borders=True))
    print()

def wait_for_target_position(ser, target_position, message="Place pieces as shown above"):
    print(message)
    print_position(target_position)
    occupied = set()

    while True:
        line = ser.readline().decode(errors='ignore').strip()
        if not line:
            continue
        board_matrix = parse_board_line(line)
        if board_matrix:
            changes = False
            for (row, col), piece in target_position.items():
                if board_matrix[row][col] == 1 and (row, col) not in occupied:
                    square_name = chess.square_name(chess.square(col, 7 - row))
                    print(f"Detected {piece} on {square_name}")
                    occupied.add((row, col))
                    changes = True
                elif board_matrix[row][col] == 0 and (row, col) in occupied:
                    square_name = chess.square_name(chess.square(col, 7 - row))
                    print(f"Removed {piece} from {square_name}")
                    occupied.remove((row, col))
                    changes = True
            if changes:
                print(f"Detected correct placements: {len(occupied)}/{len(target_position)}\n")

            # Validate: all expected squares are filled, and others are empty
            all_correct = True
            for row in range(8):
                for col in range(8):
                    expected = (row, col) in target_position
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

def main():
    parser = argparse.ArgumentParser(description="Chessboard serial reader")
    parser.add_argument("--port", "-p", required=True, help="Serial port device (e.g., /dev/ttyUSB0 or COM3)")
    parser.add_argument("--baudrate", "-b", type=int, default=115200, help="Serial port baud rate (default: 115200)")
    args = parser.parse_args()

    try:
        with serial.Serial(args.port, args.baudrate, timeout=1) as ser:
            print(f"Listening on {args.port} at {args.baudrate} baud...\n")

            # Generic position setup (e.g., initial position)
            wait_for_target_position(
                ser,
                target_position=INITIAL_POSITION_PIECES,
                message="Please set up the board to the initial position:"
            )

            # Future gameplay loop or corrections can use the same function again.
            while True:
                line = ser.readline().decode(errors='ignore').strip()
                if not line:
                    continue
                board_matrix = parse_board_line(line)
                if board_matrix:
                    print_board_with_chess(board_matrix, INITIAL_POSITION_PIECES)
    except serial.SerialException as e:
        print(f"Serial error: {e}")

if __name__ == "__main__":
    main()

