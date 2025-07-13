import argparse
import sys
import requests
from lib.LichessConnector import LichessConnector
from lib.BoardSerial import BoardSerial

REQUIRED_SCOPES = {"challenge:write", "play:write"}
#SERIAL_PORT = "/dev/ttyUSB1"
SERIAL_PORT = "/dev/ttyV1"
SERIAL_BAUDRATE = 115200

def check_token_scopes(token: str):
    url = "https://lichess.org/api/token"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            print("Error: Unable to verify token scopes. Status code:", resp.status_code)
            sys.exit(1)
        data = resp.json()
        scopes = set(data.get("scopes", "").split())
        if not REQUIRED_SCOPES.issubset(scopes):
            print(f"Error: Token is missing required permissions. Needed: {REQUIRED_SCOPES}")
            sys.exit(1)
    except requests.RequestException as e:
        print("Error: Could not check token scopes:", e)
        sys.exit(1)

class ChessApp:
    def __init__(self, token: str):
        #check_token_scopes(token)  # Check permissions first

        self.running = True
        try:
            self.lichess = LichessConnector(token)
            self.username = self.lichess.getUsername()
        except ResponseError:
            print("Error: Invalid or unauthorized token.")
            sys.exit(1)

        self.board = BoardSerial(SERIAL_PORT, SERIAL_BAUDRATE) 

    def show_menu(self):
        print(f"\nHello, {self.username}!")
        print("=== ChessApp Menu ===")
        print("1. Play on Lichess (10+5)")
        print("2. Play on the Board")
        print("3. Play on Lichess (attach to current)")
        print("Type 'q' to Exit")

    def run(self):
        while self.running:
            self.show_menu()
            choice = input("Select an option (1-3 or 'q'): ").strip().lower()

            if choice == '1':
                pass
            elif choice == '2':
                pass
            elif choice == '3':
                 game = self.lichess.findGame()

                 currentBoard = game.waitMyTurn()
                 while currentBoard != None:

                    if currentBoard.move_stack:
                        previousBoard = currentBoard.copy(stack=True)
                        last_move = previousBoard.pop()
                        san = previousBoard.san(last_move)
                        print(f"Opponent's move: \033[31m{san}\033[0m")
                    else:
                        print("You start.")

                    self.board.sync(currentBoard)
                    aMove = self.board.getMove(currentBoard)

                    #confirmation??
                    game.sendMove(aMove)
                    currentBoard = game.waitMyTurn()
            elif choice == 'q':
                print("Exiting ChessApp.")
                self.running = False
            else:
                print("Invalid choice.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the ChessApp with a Lichess token.")
    parser.add_argument('--token', required=True, help='Your Lichess API token')
    args = parser.parse_args()

    app = ChessApp(args.token)
    app.run()

