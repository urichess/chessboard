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


    def _handle_received_data(self, data: str):
        """
        Handle a single line received from the serial port.
        Only processes lines starting with 'BOARD:' and ignores all others.
        Expected format: 'BOARD:FF-FF-00-00-00-00-FF-FF'
        """
        if not data:
            return  # ignore empty lines

        data = data.strip()
        if not data.startswith("BOARD:"):
            # Ignore any line not starting with BOARD:
            # (could be firmware logs, pings, etc.)
            return

        try:
            payload = data.split("BOARD:", 1)[1].strip().upper()
            # Validate format: should be 8 hex bytes separated by '-'
            parts = payload.split("-")
            if len(parts) == 8 and all(len(p) == 2 and all(c in "0123456789ABCDEF" for c in p) for p in parts):
                self._board_message_queue.put(payload)
                # shpuld i protect currentposition? 
                #with self._pos_lock:
                self._current_position = payload
            else:
                    print(f"Ignored malformed board data: {payload}")
        except Exception as e:
            print(f"Error handling serial data '{data}': {e}")


    #def _handle_received_data(self, data):
    #    print(f"Received: {data}")
    #    if data.startswith("BOARD:"):
    #        self._board_message_queue.put(data.split("BOARD:")[1])

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

    def _diff_squares(self, prev: str, curr: str) -> list[str]:
        """
        Given two 8-byte board state strings like 'FF-FF-00-00-00-00-FF-FF',
        return a list of all squares (e.g., ['e2', 'e4']) where occupancy differs.

            Args:
            prev (str): Previous state (8 bytes separated by '-')
            curr (str): Current state (8 bytes separated by '-')

        Returns:
            list[str]: Square names that differ between the two states.
        """
        # 🛡️ Handle missing or invalid data
        if not prev or not curr:
            # Nothing to compare yet
            return []

        try:
            prev_bytes = prev.split("-")
            curr_bytes = curr.split("-")
        except AttributeError:
            # Either prev or curr wasn't a string
            return []

        if len(prev_bytes) != 8 or len(curr_bytes) != 8:
            raise ValueError("Expected exactly 8 bytes (64 bits) in each state string")

        diff = []
        bit_index = 0
        for pb, cb in zip(prev_bytes, curr_bytes):
            try:
                prev_byte = int(pb, 16)
                curr_byte = int(cb, 16)
            except ValueError:
                raise ValueError(f"Invalid hex byte in input: {pb} or {cb}")

            for i in reversed(range(8)):  # MSB = file a, LSB = file h
                prev_bit = (prev_byte >> i) & 1
                curr_bit = (curr_byte >> i) & 1
                if prev_bit != curr_bit:
                    square = chess.SQUARE_NAMES[bit_index]
                    diff.append(square)
                bit_index += 1

        return diff

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
        # Ask user to physically restore position then call sync
        print("RECOVER: " + message)
        print(board)
        print("Please place pieces back to position. Waiting for correct board state...")
        try:
            self.sync(board)
        except TimeoutError:
            print("Timeout while waiting for user to recover position.")

    
    def _recover_position(self, board: chess.Board, message: str):
        print(message)
        print(board)
        print("Please, place pieces back to position.")
        self.sync(board)
        
    def sync(self, board: chess.Board):
        ff = self._board_to_ff_format(board)

        position = self._currentPosition
        while position != ff:
            diff = self._diff_squares(position, ff)
            print(f"Synchronizing. Differing squares: {diff}")
            position = self._get_next_board_message()

        print("synchronized")
        return ff
    
    def getMove(self, board: chess.Board):
        ff_initial = self.sync(board)
        current_state = ff_initial

        recovered = False

        print("Your turn. Make your move")
        while True:

            if recovered:
                print("Recovered position. Make your move")
                current_state = ff_initial
                recovered = False

            prev_state = current_state
            current_state = self._get_next_board_message()

            if not current_state or current_state == ff_initial:
                time.sleep(0.1)
                continue

            removed, inserted = self._compare_states(ff_initial, current_state)
            removed2, inserted2 = self._compare_states(prev_state, current_state)

            if len(inserted) > 1:
                self._recover_position(board, "Illegal move: more than one piece inserted at once.")
                recovered = True
                continue

            piece_removed_from = None
            if len(removed) >= 1:
                if len(removed) > 2:
                    self._recover_position(board, "Illegal move: more than one piece removed at once.")
                    recovered = True
                    continue

                square0 = chess.parse_square(removed[0])
                piece0 = board.piece_at(square0)

                if not piece0:
                    self._recover_position(board, "Illegal move: no piece found on removed square.")
                    recovered = True
                    continue

                if len(removed) == 2:
                    square1 = chess.parse_square(removed[1])
                    piece1 = board.piece_at(square1)

                    if not piece1:
                        self._recover_position(board, "Illegal move: no piece found on removed square.")
                        recovered = True
                        continue

                    if piece0.color == piece1.color:
                        self._recover_position(board, "Illegal move: Removed two pieces of same color.")
                        recovered = True
                        continue

                    if piece0.color == board.turn:
                        piece_removed_from = removed[0]
                    elif piece1.color == board.turn:
                        piece_removed_from = removed[1]
                    else:
                        self._recover_position(board, "Illegal move: wrong color's turn. Both pieces are NOK.")
                        recovered = True
                        continue

                    print("Lifted another piece")
                else:
                    #if not piece0.color == board.turn:
                    #    color_str = "white" if piece0.color == chess.WHITE else "black"
                    #    turn_str = "white" if board.turn == chess.WHITE else "black"
                    #    self._recover_position(board, f"Illegal move: wrong color's turn. Piece color: {color_str}, Turn: {turn_str}")
                    #    recovered = True
                    #    continue

                    if piece0.color == board.turn:
                        piece_removed_from = removed[0]
                        print("Lifted player piece")
                    else:
                        print("Lifted opponent piece") #remove_from will be managed when removing player piece


            piece_inserted_at = None
            if len(inserted) == 1:
                piece_inserted_at = inserted[0]
            elif len(inserted2) == 1 and len(inserted) == 0:
                piece_inserted_at = inserted2[0]

            if piece_inserted_at:
                print ("Inserted a piece")
                if not piece_removed_from:
                    self._recover_position(board, "Illegal move: piece inserted without prior removal.")
                    recovered = True
                    continue

                move_uci = piece_removed_from + piece_inserted_at

                # check promotion
                to_square = chess.parse_square(piece_inserted_at)
                rank = chess.square_rank(to_square)

                if rank in (0, 7):
                    from_square = chess.parse_square(piece_removed_from)
                    piece = board.piece_at(from_square)

                    if piece and piece.piece_type == chess.PAWN:
                        if (piece.color == chess.WHITE and rank == 7) or (piece.color == chess.BLACK and rank == 0):
                            print ("promotion! Asuming queen...")
                            move_uci = piece_removed_from + piece_inserted_at + 'q'  # PROMOTION


                move = chess.Move.from_uci(move_uci)

                if move in board.legal_moves:
                    if board.is_castling(move):
                        bcopy = board.copy()
                        bcopy.push_uci(move_uci)
                        print ("Waitting for castles end.")
                        self.sync(bcopy)

                    print(f"Move detected: {move_uci}")
                    return move_uci
                else:
                    self._recover_position(board, f"Illegal move: {move_uci}")
                    recovered = True
                    continue

            time.sleep(0.2)
