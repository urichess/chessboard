import time

def echo_file_to_serial(file_path, serial_port="/dev/ttyV0", delay=0.2):
    try:
        with open(file_path, 'r') as f, open(serial_port, 'w') as ser:
            for line in f:
                line = line.strip()
                if line.startswith("BOARD:"):
                    ser.write(line + '\n')
                    ser.flush()
                    print(f"Sent: {line}")
                    time.sleep(delay)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python echo_to_serial.py inputfile.txt")
        exit(1)

    input_file = sys.argv[1]
    echo_file_to_serial(input_file)

