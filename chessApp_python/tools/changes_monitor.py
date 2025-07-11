import serial
import time
import chess

# Initial expected state: full pieces on ranks 1 and 2 (white), and ranks 7 and 8 (black)
INITIAL_BOARD_STATE = "FF-FF-00-00-00-00-FF-FF"
SERIAL_PORT = "/dev/ttyV1"
BAUD_RATE = 115200

def read_board_state(ser):
    """
    Reads a line from the serial port and returns the board state if in correct format.
    """
    try:
        line = ser.readline().decode('utf-8').strip()
        if line.startswith("BOARD:"):
            return line.split("BOARD:")[1]
    except Exception as e:
        print(f"Error reading from serial: {e}")
    return None

def hex_to_bit_list(hex_string):
    """
    Converts a board state string like "FF-00" into a list of 64 binary values (0 or 1).
    """
    hex_parts = hex_string.split("-")
    bits = []
    for part in hex_parts:
        bin_str = bin(int(part, 16))[2:].zfill(8)  # Convert to 8-bit binary
        bits.extend([int(b) for b in bin_str])
    return bits

def compare_states(prev, curr):
    """
    Compares two board states and prints the squares where pieces were inserted or removed.
    """
    prev_bits = hex_to_bit_list(prev)
    curr_bits = hex_to_bit_list(curr)

    if len(prev_bits) != 64 or len(curr_bits) != 64:
        print("Invalid board state length.")
        return

    for i in range(64):
        if prev_bits[i] != curr_bits[i]:
            square = chess.SQUARE_NAMES[i]
            if prev_bits[i] == 1 and curr_bits[i] == 0:
                print(f"Piece removed from {square}")
            elif prev_bits[i] == 0 and curr_bits[i] == 1:
                print(f"Piece inserted at {square}")

def wait_for_initial_position(ser):
    """
    Continuously read from serial until the initial board state is detected.
    """
    print("Please set up the chess pieces in the initial position...")
    while True:
        state = read_board_state(ser)
        if state:
            print(f"Received board state: {state}")
            if state.upper() == INITIAL_BOARD_STATE:
                print("Initial position detected!")
                return state
        time.sleep(0.5)

def main():
    print("Connecting to the chessboard via serial...")
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            previous_state = wait_for_initial_position(ser)

            board = chess.Board()
            print("Board is ready:")
            print(board)

            print("Monitoring changes...")
            while True:
                new_state = read_board_state(ser)
                if new_state and new_state != previous_state:
                    print(f"\nNew board state: {new_state}")
                    compare_states(previous_state, new_state)
                    previous_state = new_state
                time.sleep(0.2)

    except serial.SerialException as e:
        print(f"Could not open serial port: {e}")

if __name__ == "__main__":
    main()
