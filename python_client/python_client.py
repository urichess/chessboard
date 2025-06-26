import serial
import chess
import argparse

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

def print_board_with_chess(board_matrix):
    if not board_matrix:
        return

    board = chess.Board.empty()  # Start with empty board

    # The board_matrix has row 0 at top, col 0 at left
    # python-chess squares are numbered a8=0 to h1=63, so we need to map accordingly:
    # row 0 = rank 8, row 7 = rank 1
    for row in range(8):
        for col in range(8):
            if board_matrix[row][col] == 1:
                square = chess.square(col, 7 - row)  # col = file, 7-row = rank index (0-based)
                board.set_piece_at(square, chess.Piece(chess.PAWN, chess.WHITE))

    print(board.unicode(borders=True))
    print()

def main():
    parser = argparse.ArgumentParser(description="Chessboard serial reader")
    parser.add_argument(
        "--port", "-p",
        required=True,
        help="Serial port device (e.g., /dev/ttyUSB0 or COM3)"
    )
    parser.add_argument(
        "--baudrate", "-b",
        type=int,
        default=115200,
        help="Serial port baud rate (default: 115200)"
    )
    args = parser.parse_args()

    try:
        with serial.Serial(args.port, args.baudrate, timeout=1) as ser:
            print(f"Listening on {args.port} at {args.baudrate} baud...")
            while True:
                line = ser.readline().decode(errors='ignore').strip()
                if not line:
                    continue
                board_matrix = parse_board_line(line)
                if board_matrix:
                    print_board_with_chess(board_matrix)
    except serial.SerialException as e:
        print(f"Serial error: {e}")

if __name__ == "__main__":
    main()
