from lib.LichessConnector import LichessConnector
from lib.BoardSerial import BoardSerial
from lib.messages import BoardSync

SERIAL_BAUDRATE = 115200

class GameLogic:
    def __init__(self, lichess_token, serial_port, report_callback=None):
        self.report_callback = report_callback
        self.board = BoardSerial(serial_port, SERIAL_BAUDRATE)
        self.lichess = LichessConnector(lichess_token, report_callback=report_callback)
        self.game = None

    def findGame(self):
        self.game = self.lichess.findGame()
        return self.getGameInfo()
    
    def play(self):        
        currentBoard = self.game.waitMyTurn()
        while currentBoard is not None:
            if currentBoard.move_stack:
                previousBoard = currentBoard.copy(stack=True)
                last_move = previousBoard.pop()
                san = previousBoard.san(last_move)
                print(f"Opponent's move: \033[31m{san}\033[0m")

                self.board.sync(currentBoard)

                if self.report_callback:
                    self.report_callback( BoardSync(aMove=san, color="white" if previousBoard.turn else "black") )
                
            else:
                print("You start.")         

                self.board.sync(currentBoard)

            previousBoard = currentBoard.copy(stack=True)
            aMove = self.board.getMove(currentBoard)
            self.game.sendMove(aMove)
                       
            currentBoard = self.game.waitMyTurn()
        
        self.game = None

    def getGameInfo(self):
        return self.game.getGameInfo() if self.game else None
            