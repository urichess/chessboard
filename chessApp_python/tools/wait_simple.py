import serial
import time
import chess

# Expected initial board state string (8 rows from rank 8 to rank 1)
INITIAL_BOARD_STATE = "FF-FF-00-00-00-00-FF-FF"

# Serial configuration (adjust this to your port)
SERIAL_PORT = "/dev/ttyV1"  # Use something like "/dev/ttyUSB0" on Linux/macOS
BAUD_RATE = 115200

def read_board_state(ser):
    """
    Reads a line from the serial port and returns the board state if in correct format.
    Example message: "BOARD:FF-FF-00-00-00-00-FF-FF"
    """
    try:
        line = ser.readline().decode('utf-8').strip()
        if line.startswith("BOARD:"):
            state = line.split("BOARD:")[1]
            return state
    except Exception as e:
        print(f"Error reading from serial: {e}")
    return None

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
                break
        time.sleep(0.5)

def main():
    print("Connecting to the chessboard via serial...")
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            wait_for_initial_position(ser)

            # Initialize a standard chess board using python-chess
            board = chess.Board()
            print("Board is ready:")
            print(board)

            # You can continue here with move tracking, validation, etc.

    except serial.SerialException as e:
        print(f"Could not open serial port: {e}")

if __name__ == "__main__":
    main()

