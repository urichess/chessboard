import chess
import chess.pgn
import copy

def board_to_sensor_string(board):
    sensor_bytes = []
    for rank in range(0, 8):  # rank 1 to 8 (bottom to top)
        byte = 0
        for file in range(8):
            sq = chess.square(file, rank)
            if board.piece_at(sq) is not None:
                byte |= (1 << (7 - file))  # MSB = file a
        sensor_bytes.append(byte)
    return '-'.join(f"{b:02X}" for b in sensor_bytes)

def generate_detailed_sensor_output_from_pgn(pgn_file_path):
    with open(pgn_file_path, 'r') as pgn_file:
        game = chess.pgn.read_game(pgn_file)
        if game is None:
            print("No games found in PGN file.")
            return

        board = game.board()
        print(f"BOARD:{board_to_sensor_string(board)}")  # initial position

        for move in game.mainline_moves():
            board_before_move = copy.deepcopy(board)

            from_sq = move.from_square
            to_sq = move.to_square

            # Remove piece from from_sq (simulate lifting)
            board_before_move.remove_piece_at(from_sq)
            print(f"BOARD:{board_to_sensor_string(board_before_move)}")

            # Place piece at to_sq (simulate placing)
            board.push(move)
            print(f"BOARD:{board_to_sensor_string(board)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python generate_detailed_from_pgn.py yourgame.pgn")
        exit(1)

    generate_detailed_sensor_output_from_pgn(sys.argv[1])

