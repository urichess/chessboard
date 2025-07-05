import serial
import time
import chess

INITIAL_BOARD_STATE = "FF-FF-00-00-00-00-FF-FF"
#SERIAL_PORT = "/dev/ttyV1"
SERIAL_PORT = "/dev/ttyUSB1"
BAUD_RATE = 115200

def read_board_state(ser):
    try:
        line = ser.readline().decode('utf-8').strip()
        if line.startswith("BOARD:"):
            return line.split("BOARD:")[1]
    except Exception as e:
        print(f"Error reading from serial: {e}")
    return None

def hex_to_bit_list(hex_string):
    hex_parts = hex_string.split("-")
    bits = []
    for part in hex_parts:
        bin_str = bin(int(part, 16))[2:].zfill(8)
        bits.extend([int(b) for b in bin_str])
    return bits

def compare_states(prev, curr):
    prev_bits = hex_to_bit_list(prev)
    curr_bits = hex_to_bit_list(curr)
    removed = []
    inserted = []

    for i in range(64):
        if prev_bits[i] != curr_bits[i]:
            square = chess.SQUARE_NAMES[i]
            if prev_bits[i] == 1 and curr_bits[i] == 0:
                removed.append(square)
            elif prev_bits[i] == 0 and curr_bits[i] == 1:
                inserted.append(square)
    return removed, inserted

def wait_for_initial_position(ser):
    print("Please set up the chess pieces in the initial position...")
    while True:
        state = read_board_state(ser)
        if state:
            print(f"Received board state: {state}")
            if state.upper() == INITIAL_BOARD_STATE:
                print("Initial position detected!")
                return state
        time.sleep(0.5)

def board_to_ff_format(board):
    """
    Converts a python-chess board to the BOARD:XX-XX-... format,
    where each rank is encoded as 8 bits (1 = occupied, 0 = empty),
    ordered from rank 1 (bottom) to rank 8 (top).
    """
    ranks = []
    for rank in range(1, 9):  # rank 1 to 8
        bits = ''
        for file in range(8):  # files a to h
            square = chess.square(file, rank - 1)
            bits += '1' if board.piece_at(square) else '0'
        hex_value = '{:02X}'.format(int(bits, 2))
        ranks.append(hex_value)
    return "-".join(ranks)
    #return "BOARD:" + "-".join(ranks)


def wait_board(ser, expected_state):
    while True:
        state = read_board_state(ser)
        if state and state.upper() == expected_state:
            return
        time.sleep(0.2)

def wait_until_board_matches(ser, expected_state):
    print("Waiting for board to return to the correct state...")
    wait_board(ser, expected_state)
    print("Board restored to valid state.")

def wait_end_castling(ser, expected_state):
    print("Waitting Castles end move...")
    wait_board(ser, expected_state)
    print("Castles ended.")
    

def main():
    print("Connecting to the chessboard via serial...")
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            last_valid_state = wait_for_initial_position(ser)
            current_state = last_valid_state
            board = chess.Board()
            print("Board is ready:")
            print(board)

            piece_removed_from = None

            while True:
                prev_state = current_state
                current_state = read_board_state(ser)
                if not current_state or current_state == last_valid_state:
                    time.sleep(0.1)
                    continue

                removed, inserted = compare_states(last_valid_state, current_state)
                removed2, inserted2 = compare_states(prev_state, current_state)
                

                # Illegal: more than one piece removed
                #if len(removed) > 1:
                #    print("Illegal move: more than one piece removed at once.")
                #    print(board)
                #    wait_until_board_matches(ser, last_valid_state)
                #    piece_removed_from = None
                #    continue

                # Illegal: more than one piece inserted
                if len(inserted) > 1:
                    print("Illegal move: more than one piece inserted at once.")
                    print(board)
                    wait_until_board_matches(ser, last_valid_state)
                    piece_removed_from = None
                    continue

                piece_removed_from = None
                if len(removed) >= 1:
                    if len(removed) > 2:
                        print("Illegal move: more than one piece removed at once.")
                        print(board)
                        wait_until_board_matches(ser, last_valid_state)
                        piece_removed_from = None
                        continue

                    square0 = chess.parse_square(removed[0])
                    piece0 = board.piece_at(square0)

                    if not piece0:
                        print("Illegal move: no piece found on removed square.")
                        print(board)
                        wait_until_board_matches(ser, last_valid_state)
                        continue

                    if len(removed) == 2: # CAPTURE
                        print ("Capture?")
                        square1 = chess.parse_square(removed[1])
                        piece1 = board.piece_at(square1)

                        if not piece1:
                            print("Illegal move: no piece found on removed square.")
                            print(board)
                            wait_until_board_matches(ser, last_valid_state)
                            continue

                        if piece0.color == piece1.color:
                            print("Illegal move: Removed two pieces of same color.")
                            print(board)
                            wait_until_board_matches(ser, last_valid_state)
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
                            wait_until_board_matches(ser, last_valid_state)
                            continue
                    else:
                        if not piece0.color == board.turn:
                            color_str = "white" if piece0.color == chess.WHITE else "black"
                            turn_str = "white" if board.turn == chess.WHITE else "black"
                            print(f"Illegal move: wrong color's turn. Piece color: {color_str}, Turn: {turn_str}")
                            print(board)
                            wait_until_board_matches(ser, last_valid_state)
                            continue

                        piece_removed_from = removed[0]
                        print(f"Piece lifted from {piece_removed_from}...")


                piece_inserted_at = None
                if len(inserted) == 1:
                    piece_inserted_at = inserted[0]

                if len(inserted2) == 1 and len(inserted) == 0: #Capture... have to find a better way. maybe with magnetos orientation
                    piece_inserted_at = inserted2[0]


                if piece_inserted_at:
                    if not piece_removed_from:
                        print("Illegal move: piece inserted without prior removal.")
                        print(board)
                        wait_until_board_matches(ser, last_valid_state)
                        continue

                    move_uci = piece_removed_from + piece_inserted_at
                    move = chess.Move.from_uci(move_uci)
                    if move in board.legal_moves:
                        castling = board.is_castling(move)
                        board.push(move)
                        print(f"Move played: {move_uci}")
                        print(board)                        

                        last_valid_state = current_state
                        piece_removed_from = None

                        if castling:
                            current_state = board_to_ff_format (board)
                            print ("state: "+current_state)
                            last_valid_state = current_state
                            wait_end_castling(ser, last_valid_state)
                            
                    else:
                        print(f"Illegal move: {move_uci}")
                        print(board)
                        wait_until_board_matches(ser, last_valid_state)
                        piece_removed_from = None

                if len(removed) == 0 and len(inserted) == 0:
                    # No change
                    pass

                time.sleep(0.2)

    except serial.SerialException as e:
        print(f"Could not open serial port: {e}")

if __name__ == "__main__":
    main()
