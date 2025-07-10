import serial
import time
import chess

class BoardSerial:
    def __init__(self, port: str, baudrate: int):
        self.port = port
        self.baudrate = baudrate
        self.connection = None
        self.open_connection()

    def open_connection(self):
        try:
            self.connection = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"Connected to {self.port} at {self.baudrate} baud.")
        except serial.SerialException as e:
            print(f"Failed to connect to {self.port}: {e}")
            self.connection = None

    def close_connection(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("Serial connection closed.")

    def _readCurrentPosition(self):
        try:
            line = self.connection.readline().decode('utf-8').strip()
            if line.startswith("BOARD:"):
                return line.split("BOARD:")[1]
        except Exception as e:
            print(f"Error reading from serial: {e}")
        return None

    def wait_board(self, expected_state):
        while True:
            try:
                line = self.connection.readline().decode('utf-8').strip()
                if line.startswith("BOARD:"):
                    state = line.split("BOARD:")[1]
                    if state.upper() == expected_state:
                        return
            except Exception as e:
                print(f"Error while waiting for board: {e}")
            time.sleep(0.2)

    def wait_until_board_matches(self, expected_state):
        print("Waiting for board to return to the correct state...")
        self.wait_board(expected_state)
        print("Board restored to valid state.")

    def wait_end_castling(self, expected_state):
        print("Waiting for castling to complete...")
        self.wait_board(expected_state)
        print("Castling complete.")

    def board_to_ff_format(self, board: chess.Board) -> str:
        ranks = []
        for rank in range(1, 9):  # rank 1 to 8
            bits = ''
            for file in range(8):  # file a to h
                square = chess.square(file, rank - 1)
                bits += '1' if board.piece_at(square) else '0'
            hex_value = '{:02X}'.format(int(bits, 2))
            ranks.append(hex_value)
        return "-".join(ranks)

    def compare_states(self, old_state: str, new_state: str):
        """
        Dummy placeholder: you must replace this with your actual comparison logic.
        Returns two lists: removed squares and inserted squares.
        """
        return [], []

    def waitPosition(self, expected_state: str):
        while True:
            state = self._readCurrentPosition()
            if state and state.upper() == expected_state:
                return
            time.sleep(0.2)

    def getMove(self, board: chess.Board):
        piece_removed_from = None
        last_valid_state = self._readCurrentPosition()
        current_state = last_valid_state

        while True:
            prev_state = current_state
            current_state = self._readCurrentPosition()

            if not current_state or current_state == last_valid_state:
                time.sleep(0.1)
                continue

            removed, inserted = self.compare_states(last_valid_state, current_state)
            removed2, inserted2 = self.compare_states(prev_state, current_state)

            if len(inserted) > 1:
                print("Illegal move: more than one piece inserted at once.")
                print(board)
                self.wait_until_board_matches(last_valid_state)
                piece_removed_from = None
                continue

            piece_removed_from = None
            if len(removed) >= 1:
                if len(removed) > 2:
                    print("Illegal move: more than one piece removed at once.")
                    print(board)
                    self.wait_until_board_matches(last_valid_state)
                    continue

                square0 = chess.parse_square(removed[0])
                piece0 = board.piece_at(square0)

                if not piece0:
                    print("Illegal move: no piece found on removed square.")
                    print(board)
                    self.wait_until_board_matches(last_valid_state)
                    continue

                if len(removed) == 2:
                    square1 = chess.parse_square(removed[1])
                    piece1 = board.piece_at(square1)

                    if not piece1:
                        print("Illegal move: no piece found on removed square.")
                        print(board)
                        self.wait_until_board_matches(last_valid_state)
                        continue

                    if piece0.color == piece1.color:
                        print("Illegal move: Removed two pieces of same color.")
                        print(board)
                        self.wait_until_board_matches(last_valid_state)
                        continue

                    if piece0.color == board.turn:
                        piece_removed_from = removed[0]
                        print(f"Piece lifted from {piece_removed_from}...")
                    elif piece1.color == board.turn:
                        piece_removed_from = removed[1]
                        print(f"Piece lifted from {piece_removed_from}...")
                    else:
                        print("Illegal move: wrong color's turn. Both pieces are NOK.")
                        print(board)
                        self.wait_until_board_matches(last_valid_state)
                        continue
                else:
                    if not piece0.color == board.turn:
                        color_str = "white" if piece0.color == chess.WHITE else "black"
                        turn_str = "white" if board.turn == chess.WHITE else "black"
                        print(f"Illegal move: wrong color's turn. Piece color: {color_str}, Turn: {turn_str}")
                        print(board)
                        self.wait_until_board_matches(last_valid_state)
                        continue

                    piece_removed_from = removed[0]
                    print(f"Piece lifted from {piece_removed_from}...")

            piece_inserted_at = None
            if len(inserted) == 1:
                piece_inserted_at = inserted[0]
            elif len(inserted2) == 1 and len(inserted) == 0:
                piece_inserted_at = inserted2[0]

            if piece_inserted_at:
                if not piece_removed_from:
                    print("Illegal move: piece inserted without prior removal.")
                    print(board)
                    self.wait_until_board_matches(last_valid_state)
                    continue

                move_uci = piece_removed_from + piece_inserted_at
                move = chess.Move.from_uci(move_uci)

                if move in board.legal_moves:
                    print(f"Move detected: {move_uci}")
                    return move_uci
                else:
                    print(f"Illegal move: {move_uci}")
                    print(board)
                    self.wait_until_board_matches(last_valid_state)
                    continue

            time.sleep(0.2)

    def __del__(self):
        self.close_connection()

