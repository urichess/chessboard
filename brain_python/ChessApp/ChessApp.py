import argparse
import sys
import requests
import berserk
from berserk.exceptions import ResponseError

REQUIRED_SCOPES = {"challenge:write", "play:write"}

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
        self.session = berserk.TokenSession(token)
        self.client = berserk.Client(session=self.session)

        try:
            user = self.client.account.get()
            self.username = user['username']
        except ResponseError:
            print("Error: Invalid or unauthorized token.")
            sys.exit(1)

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
                pass
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

