from lib.LichessConnector import LichessConnector
from lib.BoardSerial import BoardSerial

SERIAL_BAUDRATE = 115200

class GameLogic:
    def __init__(self, lichess_token, serial_port):
        self.board = BoardSerial(serial_port, SERIAL_BAUDRATE) 
        self.lichess = LichessConnector(lichess_token)
        #username = self.lichess.getUsername()    
        
        #self.game = self.lichess.findGame()
    
    def play(self):
        game = self.lichess.findGame()
        gameid = game.game_id
        
        currentBoard = game.waitMyTurn()
        while currentBoard is not None:
            if currentBoard.move_stack:
                previousBoard = currentBoard.copy(stack=True)
                last_move = previousBoard.pop()
                san = previousBoard.san(last_move)
                print(f"Opponent's move: \033[31m{san}\033[0m")
                
            else:
                print("You start.")

            self.board.sync(currentBoard)

            previousBoard = currentBoard.copy(stack=True)
            aMove = self.board.getMove(currentBoard)
            game.sendMove(aMove)
                       
            currentBoard = game.waitMyTurn()
