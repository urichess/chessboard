from BoardSerial import BoardSerial
import chess


SERIAL_PORT = "/dev/ttyV1"
SERIAL_BAUDRATE = 115200

bs = BoardSerial(SERIAL_PORT, SERIAL_BAUDRATE)

INITIAL_POSITION = "FF-FF-00-00-00-00-FF-FF"

# wait for initial position
board = chess.Board()

print ("Place pieces in initial position")
print (board)
bs.sync(board)

print ("Ready!!! You can now make moves") 

while True:
    uci_move = bs.getMove(board)

    move = chess.Move.from_uci(uci_move)

    sanMove = board.san(move)
    board.push(move)
    print ("Moved: ", sanMove)
    print (board)

