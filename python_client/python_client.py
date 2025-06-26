import serial

def parse_board_line(line):
    if not line.startswith("BOARD:"):
        return None

    try:
        hex_part = line.strip().split("BOARD:")[1]
        hex_bytes = hex_part.split('-')
        if len(hex_bytes) != 8:
            return None

        board = []
        for byte_str in hex_bytes:
            byte = int(byte_str, 16)
            row = [(byte >> (7 - i)) & 1 for i in range(8)]
            board.append(row)
        return board
    except Exception as e:
        print(f"Error parsing line: {e}")
        return None

def print_board(board):
    if not board:
        return
    print("⬇️  Board (Row 0 at top, Col 0 at left):")
    for row in board:
        print(' '.join('●' if cell else '.' for cell in row))
    print()

def main():
    port = '/dev/ttyUSB0'  # Change as needed (e.g., COM3 on Windows)
    baudrate = 115200      # Set to match STM32 UART
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            print(f"Listening on {port} at {baudrate} baud...")
            while True:
                line = ser.readline().decode(errors='ignore').strip()
                if not line:
                    continue
                board = parse_board_line(line)
                if board:
                    print_board(board)
    except serial.SerialException as e:
        print(f"Serial error: {e}")

if __name__ == "__main__":
    main()

