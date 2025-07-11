import serial
import time
import chess

class BoardSerial:
    def __init__(self, port: str, baudrate: int):
        self.port = port
        self.baudrate = baudrate
        self.connection = None
        self._open_connection()

    def _open_connection(self):
        try:
            self.connection = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"Connected to {self.port} at {self.baudrate} baud.")
        except serial.SerialException as e:
            print(f"Failed to connect to {self.port}: {e}")
            self.connection = None

    def _close_connection(self):
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

    def _wait_board(self, expected_state):
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

    def _recover_position(self, board: chess.Board, message: str):
        print(message)
        print(board)
        print("Please, place pieces back to position.")
        self.sync(board)

    def wait_end_castling(self, expected_state):
        print("Waiting for castling to complete...")
        self._wait_board(expected_state)
        print("Castling complete.")

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

    def getMove(self, board: chess.Board):
        self.sync(board)

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
                else:
                    if not piece0.color == board.turn:
                        color_str = "white" if piece0.color == chess.WHITE else "black"
                        turn_str = "white" if board.turn == chess.WHITE else "black"
                        self._recover_position(board, f"Illegal move: wrong color's turn. Piece color: {color_str}, Turn: {turn_str}")
                        continue

                    piece_removed_from = removed[0]

            piece_inserted_at = None
            if len(inserted) == 1:
                piece_inserted_at = inserted[0]
            elif len(inserted2) == 1 and len(inserted) == 0:
                piece_inserted_at = inserted2[0]

            if piece_inserted_at:
                if not piece_removed_from:
                    self._recover_position(board, "Illegal move: piece inserted without prior removal.")
                    continue

                move_uci = piece_removed_from + piece_inserted_at
                move = chess.Move.from_uci(move_uci)

                if move in board.legal_moves:
                    if move.is_castling():
                        board.push_uci(move_uci)
                        print ("Wait castles end.")
                        self.sync(board)

                    print(f"Move detected: {move_uci}")
                    return move_uci
                else:
                    self._recover_position(board, f"Illegal move: {move_uci}")
                    continue

            time.sleep(0.2)

    def sync(self, board: chess.Board):
        ff = self._board_to_ff_format(board)
        self._wait_board(ff)

    def __del__(self):
        self._close_connection()
