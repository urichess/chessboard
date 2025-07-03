import serial
import time
import chess

INITIAL_BOARD_STATE = "FF-FF-00-00-00-00-FF-FF"
SERIAL_PORT = "/dev/ttyV1"  # or "/dev/ttyUSB0"
BAUD_RATE = 115200

def parse_board_state(state_str):
    """
    Parses the hex board string into a list of 64 booleans (True = occupied).
    """
    bytes_str = state_str.split('-')
    board_bits = []
    for byte in bytes_str:
        bits = bin(int(byte, 16))[2:].zfill(8)
        board_bits.extend([bit == '1' for bit in bits])
    return board_bits

def read_board_state(ser):
    try:
        line = ser.readline().decode('utf-8').strip()
        if line.startswith("BOARD:"):
            return line.split("BOARD:")[1]
    except Exception as e:
        print(f"Serial read error: {e}")
    return None

def find_move(prev_state, curr_state):
    """
    Finds the from_square and to_square based on board change.
    """
    changed = [(i, prev_state[i], curr_state[i]) for i in range(64) if prev_state[i] != curr_state[i]]

    if len(changed) != 2:
        return (None, None)

    from_sq = next(i for i, before, after in changed if before and not after)
    to_sq = next(i for i, before, after in changed if not before and after)

    return (from_sq, to_sq)

def wait_for_move(ser, board, last_state_bits):
    print("Waiting for moves...")
    while True:
        state_str = read_board_state(ser)
        if not state_str:
            continue

        new_state_bits = parse_board_state(state_str)
        from_sq, to_sq = find_move(last_state_bits, new_state_bits)

        if from_sq is not None and to_sq is not None:
            possible_moves = [m for m in board.legal_moves if m.from_square == from_sq and m.to_square == to_sq]

            if len(possible_moves) == 0:
                print(f"Illegal move: {chess.square_name(from_sq)} to {chess.square_name(to_sq)}")
            elif len(possible_moves) == 1:
                move = possible_moves[0]
                if board.is_legal(move):
                    san_move = board.san(move)  # get SAN before pushing
                    board.push(move)
                    print(f"Move: {san_move} ({move.uci()})")
                    print(board)
                    last_state_bits = new_state_bits
            else:
                # Multiple moves possible - likely promotion.
                # Automatically promote to queen.
                move = chess.Move(from_sq, to_sq, promotion=chess.QUEEN)
                if move in board.legal_moves:
                    board.push(move)
                    print(f"Promotion to Queen move: {board.san(move)} ({move.uci()})")
                    print(board)
                    last_state_bits = new_state_bits
                else:
                    print("Invalid promotion move.")

        time.sleep(0.1)

def main():
    print("Connecting to the board...")
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            print("Waiting for initial position...")
            while True:
                state_str = read_board_state(ser)
                if state_str and state_str.upper() == INITIAL_BOARD_STATE:
                    print("Initial position detected!")
                    break
                time.sleep(0.5)

            board = chess.Board()
            last_state_bits = parse_board_state(INITIAL_BOARD_STATE)

            wait_for_move(ser, board, last_state_bits)

    except serial.SerialException as e:
        print(f"Serial connection error: {e}")

if __name__ == "__main__":
    main()

