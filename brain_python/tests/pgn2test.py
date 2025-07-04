import chess
import chess.pgn
import sys

def get_sensor_bitmap(board):
    # Returns a 64-element list: 1 if square occupied, 0 otherwise
    return [1 if board.piece_at(sq) else 0 for sq in chess.SQUARES]

def format_board_line(bits):
    # Converts 64 bits (a1-h8) into BOARD:XX-...-XX line (rank1 to rank8)
    hex_ranks = []
    for r in range(8):
        byte = 0
        for f in range(8):
            idx = r * 8 + f
            byte = (byte << 1) | bits[idx]
        hex_ranks.append(f"{byte:02X}")
    return "BOARD:" + "-".join(hex_ranks)

def apply_move_to_bitmap(bits, from_sq=None, to_sq=None, remove_sq=None):
    # Create a copy of the board bitmap and apply changes
    new_bits = bits[:]
    if from_sq is not None:
        new_bits[from_sq] = 0
    if remove_sq is not None:
        new_bits[remove_sq] = 0
    if to_sq is not None:
        new_bits[to_sq] = 1
    return new_bits

def generate_board_lines_from_game(game):
    board = chess.Board()
    lines = []

    # 0. Emit initial position
    initial_bitmap = get_sensor_bitmap(board)
    lines.append(format_board_line(initial_bitmap))

    for move in game.mainline_moves():
        from_sq = move.from_square
        to_sq = move.to_square
        capture = board.is_capture(move)
        is_castling = board.is_castling(move)

        current_bitmap = get_sensor_bitmap(board)

        # 1. Remove moving piece from origin
        bitmap1 = apply_move_to_bitmap(current_bitmap, from_sq=from_sq)
        lines.append(format_board_line(bitmap1))

        # 2. Remove captured piece from destination (if capture and not castling)
        if capture and not is_castling:
            bitmap2 = apply_move_to_bitmap(bitmap1, remove_sq=to_sq)
            lines.append(format_board_line(bitmap2))
        else:
            bitmap2 = bitmap1

        # 3. Place piece on destination (after promotion if any)
        bitmap3 = apply_move_to_bitmap(bitmap2, to_sq=to_sq)
        lines.append(format_board_line(bitmap3))

        # 4. If castling, move rook
        if is_castling:
            if move.to_square == chess.G1:  # white kingside
                rook_from, rook_to = chess.H1, chess.F1
            elif move.to_square == chess.C1:  # white queenside
                rook_from, rook_to = chess.A1, chess.D1
            elif move.to_square == chess.G8:  # black kingside
                rook_from, rook_to = chess.H8, chess.F8
            elif move.to_square == chess.C8:  # black queenside
                rook_from, rook_to = chess.A8, chess.D8
            else:
                raise ValueError("Invalid castling move")

            bitmap4 = apply_move_to_bitmap(bitmap3, from_sq=rook_from)
            lines.append(format_board_line(bitmap4))
            bitmap5 = apply_move_to_bitmap(bitmap4, to_sq=rook_to)
            lines.append(format_board_line(bitmap5))

        board.push(move)

    return lines

def main():
    if len(sys.argv) < 2:
        print("Usage: python pgn_to_board_lines.py game.pgn")
        sys.exit(1)

    pgn_path = sys.argv[1]

    with open(pgn_path) as f:
        game = chess.pgn.read_game(f)

    board_lines = generate_board_lines_from_game(game)

    for line in board_lines:
        print(line)

if __name__ == "__main__":
    main()

