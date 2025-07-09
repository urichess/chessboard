import threading
import serial

class SerialHandler:
    def __init__(self, port, baudrate=9600, timeout=1, debug=False):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.debug = debug

        self.serial_port = None
        self.running = False
        self.thread = None
        self.callback = None

    def set_callback(self, callback):
        """Sets a function to be called with parsed board data."""
        self.callback = callback

    def start(self):
        """Opens serial port and starts the reading thread."""
        try:
            self.serial_port = serial.Serial(
                self.port, 
                self.baudrate, 
                timeout=self.timeout
            )
            self.running = True
            self.thread = threading.Thread(target=self._read_loop, daemon=True)
            self.thread.start()
        except Exception as e:
            print("[SerialHandler] Failed to open serial port:", e)

    def stop(self):
        """Stops reading and closes the serial port."""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

    def _read_loop(self):
        """Reads from serial and processes incoming data."""
        while self.running:
            try:
                line = self.serial_port.readline()
                if not line:
                    break  # Exit on empty line for testing or disconnected port

                decoded_line = line.decode('utf-8').strip()

                if self.debug:
                    print(f"[SerialHandler] Received: {decoded_line}")

                if decoded_line.startswith("BOARD:"):
                    if self.callback:
                        self.callback(decoded_line)
            except Exception as e:
                if self.debug:
                    print("[SerialHandler] Error reading serial:", e)


