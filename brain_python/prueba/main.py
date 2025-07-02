# main.py

import argparse
from serial_reader import SerialChessReader

def main():
    parser = argparse.ArgumentParser(description="Chessboard serial reader")
    parser.add_argument("--port", "-p", required=True, help="Serial port device (e.g., /dev/ttyUSB0)")
    parser.add_argument("--baudrate", "-b", type=int, default=115200, help="Baud rate")
    args = parser.parse_args()

    reader = SerialChessReader(args.port, args.baudrate)
    reader.run()

if __name__ == "__main__":
    main()
