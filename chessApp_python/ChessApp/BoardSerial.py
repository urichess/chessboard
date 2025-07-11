import serial
import threading
import time
import queue
import chess

class BoardSerial:
    def __init__(self, port, baudrate):
        self._port = port
        self._baudrate = baudrate
        self._connection = None
        self._read_thread = None
        self._stop_thread = threading.Event()
        self._board_message_queue = queue.Queue()
        self._currentPosition = None

        self._connect()

    def __del__(self):
        self._disconnect()

    def _connect(self):
        try:
            self._connection = serial.Serial(self._port, self._baudrate, timeout=1)
            print(f"Connected to {self._port} at {self._baudrate} baud.")
            self._stop_thread.clear()
            self._read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self._read_thread.start()
        except serial.SerialException as e:
            print(f"Failed to connect: {e}")
            self._connection = None

    def _disconnect(self):
        self._stop_thread.set()
        if self._read_thread and self._read_thread.is_alive():
            self._read_thread.join()
        if self._connection and self._connection.is_open:
            self._connection.close()
            print(f"Disconnected from {self._port}.")

    def _send_data(self, data):
        if self._connection and self._connection.is_open:
            self._connection.write(data.encode())
        else:
            print("No open connection to send data.")

    def _read_loop(self):
        while not self._stop_thread.is_set():
            if self._connection and self._connection.in_waiting:
                try:
                    line = self._connection.readline().decode().strip()
                    self._handle_received_data(line)
                except Exception as e:
                    print(f"Error reading from serial: {e}")
            time.sleep(0.1)

    def _handle_received_data(self, data):
        print(f"Received: {data}")
        if data.startswith("BOARD:"):
            self._board_message_queue.put(data.split("BOARD:")[1])

    def _get_next_board_message(self, timeout=None):
        try:
            self._currentPosition = self._board_message_queue.get(timeout=timeout)
            return self._currentPosition
        except queue.Empty:
            self._currentPosition = None

        self._currentPosition
        
    def _board_to_ff_format(self, board: chess.Board) -> str:
        ranks = []
        for rank in range(1, 9):  # rank 1 to 8
            bits = ''
            for file in range(8):  # file a to h
                square = chess.square(file, rank - 1)
                bits += '1' if board.piece_at(square) else '0'
            hex_value = '{:02X}'.format(int(bits, 2))
            ranks.append(hex_value)
        return "-".join(ranks)

    @staticmethod    
    def _compare_states(prev, curr):
        """
        Compares two 64-bit board states (e.g., 'FF-FF-00-00-00-00-FF-FF') and returns
        squares where pieces were inserted or removed.

        Args:
            prev (str): Previous state as 'FF-FF-...'
            curr (str): Current state as 'FF-FF-...'

        Returns:
            (removed, inserted): Tuple of lists of square names
        """
        prev_bytes = prev.split("-")
        curr_bytes = curr.split("-")

        if len(prev_bytes) != 8 or len(curr_bytes) != 8:
            raise ValueError("Expected exactly 8 bytes (64 bits) in board state.")

        removed = []
        inserted = []

        bit_index = 0
        for pb, cb in zip(prev_bytes, curr_bytes):
            try:
                prev_byte = int(pb, 16)
                curr_byte = int(cb, 16)
            except ValueError:
                raise ValueError(f"Invalid hex byte: '{pb}' or '{cb}'")

            for i in reversed(range(8)):  # MSB first
                prev_bit = (prev_byte >> i) & 1
                curr_bit = (curr_byte >> i) & 1

                if prev_bit != curr_bit:
                    square = chess.SQUARE_NAMES[bit_index]
                    if prev_bit == 1 and curr_bit == 0:
                        removed.append(square)
                    elif prev_bit == 0 and curr_bit == 1:
                        inserted.append(square)

                bit_index += 1

        return removed, inserted


    
    def _recover_position(self, board: chess.Board, message: str):
        print(message)
        print(board)
        print("Please, place pieces back to position.")
        self.sync(board)
        
    def sync(self, board: chess.Board):
        ff = self._board_to_ff_format(board)

        position = self._currentPosition
        while position != ff:
            position = self._get_next_board_message()

        print("synchronized")
        return ff
    
    def getMove(self, board: chess.Board):
        last_valid_state = self.sync(board)
        current_state = last_valid_state
        piece_removed_from = None

        while True:
            prev_state = current_state
            current_state = self._get_next_board_message()

            if not current_state or current_state == last_valid_state:
                time.sleep(0.1)
                continue

            removed, inserted = self._compare_states(last_valid_state, current_state)
            removed2, inserted2 = self._compare_states(prev_state, current_state)

            if len(inserted) > 1:
                self._recover_position(board, "Illegal move: more than one piece inserted at once.")
                piece_removed_from = None
                continue

            piece_removed_from = None
            if len(removed) >= 1:
                if len(removed) > 2:
                    self._recover_position(board, "Illegal move: more than one piece removed at once.")
                    continue

                square0 = chess.parse_square(removed[0])
                piece0 = board.piece_at(square0)

                if not piece0:
                    self._recover_position(board, "Illegal move: no piece found on removed square.")
                    continue

                if len(removed) == 2:
                    square1 = chess.parse_square(removed[1])
                    piece1 = board.piece_at(square1)

                    if not piece1:
                        self._recover_position(board, "Illegal move: no piece found on removed square.")
                        continue

                    if piece0.color == piece1.color:
                        self._recover_position(board, "Illegal move: Removed two pieces of same color.")
                        continue

                    if piece0.color == board.turn:
                        piece_removed_from = removed[0]
                    elif piece1.color == board.turn:
                        piece_removed_from = removed[1]
                    else:
                        self._recover_position(board, "Illegal move: wrong color's turn. Both pieces are NOK.")
                        continue

                    print("Lifted another piece")
                else:
                    if not piece0.color == board.turn:
                        color_str = "white" if piece0.color == chess.WHITE else "black"
                        turn_str = "white" if board.turn == chess.WHITE else "black"
                        self._recover_position(board, f"Illegal move: wrong color's turn. Piece color: {color_str}, Turn: {turn_str}")
                        continue

                    piece_removed_from = removed[0]
                    print("Lifted a piece")

            piece_inserted_at = None
            if len(inserted) == 1:
                piece_inserted_at = inserted[0]
            elif len(inserted2) == 1 and len(inserted) == 0:
                piece_inserted_at = inserted2[0]

            if piece_inserted_at:
                print ("Inserted a piece")
                if not piece_removed_from:
                    self._recover_position(board, "Illegal move: piece inserted without prior removal.")
                    continue

                move_uci = piece_removed_from + piece_inserted_at
                move = chess.Move.from_uci(move_uci)

                if move in board.legal_moves:
                    if board.is_castling(move):
                        board.push_uci(move_uci)
                        print ("Wait castles end.")
                        self.sync(board)

                    print(f"Move detected: {move_uci}")
                    return move_uci
                else:
                    self._recover_position(board, f"Illegal move: {move_uci}")
                    continue

            time.sleep(0.2)
